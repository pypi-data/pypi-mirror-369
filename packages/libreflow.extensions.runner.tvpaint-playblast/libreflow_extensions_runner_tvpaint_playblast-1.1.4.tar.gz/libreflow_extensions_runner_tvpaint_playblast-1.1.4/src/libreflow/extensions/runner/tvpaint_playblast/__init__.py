import os
import subprocess
import re

from kabaret import flow
from kabaret.flow_contextual_dict import get_contextual_dict
from libreflow.baseflow.file import (
    GenericRunAction,
    TrackedFile,
    TrackedFolder,
    FileRevisionNameChoiceValue,
    MarkImageSequence,
    FileJob,
    WaitProcess,
)
from libreflow.baseflow.task import Task
from libreflow.baseflow.site import SiteJobsPoolNames
from libreflow.utils.os import remove_folder_content


class RenderQualityChoiceValue(flow.values.ChoiceValue):
    CHOICES = ["Final"]  # ['Preview','Final']


class RenderTvPaintPlayblast(flow.Action):
    ICON = ("icons.libreflow", "tvpaint")

    _file = flow.Parent()
    _files = flow.Parent(2)
    _task = flow.Parent(3)
    _shot = flow.Parent(5)
    _sequence = flow.Parent(7)

    revision = flow.Param(None, FileRevisionNameChoiceValue)
    render_quality = flow.Param("Final", RenderQualityChoiceValue)

    with flow.group("Advanced settings"):
        start_frame = flow.IntParam()
        end_frame = flow.IntParam()
        show_reference = flow.BoolParam(False)
        keep_existing_frames = flow.BoolParam(True)

    def allow_context(self, context):
        return context and self._file.format.get() == "tvpp"

    def get_buttons(self):
        if self._task.name() == "exposition":
            self.show_reference.set(True)

        self.revision.revert_to_default()
        self.start_frame.revert_to_default()
        self.end_frame.revert_to_default()
        return ["Render", "Cancel"]

    def ensure_render_folder(self):
        folder_name = self._file.display_name.get().split(".")[0]
        folder_name += "_render"
        if self.render_quality.get() == "Preview":
            folder_name += "_preview"

        if not self._files.has_folder(folder_name):
            self._files.create_folder_action.folder_name.set(folder_name)
            self._files.create_folder_action.category.set("Outputs")
            self._files.create_folder_action.tracked.set(True)
            self._files.create_folder_action.run(None)

        return self._files[folder_name]

    def ensure_render_folder_revision(self):
        folder = self.ensure_render_folder()
        revision_name = self.revision.get()
        source_revision = self._file.get_revision(self.revision.get())

        if not folder.has_revision(revision_name):
            revision = folder.add_revision(revision_name)
            folder.set_current_user_on_revision(revision_name)
        else:
            revision = folder.get_revision(revision_name)

        revision.comment.set(source_revision.comment.get())

        folder.ensure_last_revision_oid()

        self._files.touch()

        return revision

    def start_tvpaint(self, path):
        start_action = self._task.start_tvpaint
        start_action.file_path.set(path)
        ret = start_action.run(None)
        self.tvpaint_runner = (
            self.root()
            .session()
            .cmds.SubprocessManager.get_runner_info(ret["runner_id"])
        )

    def execute_render_script(
        self, path, start_frame, end_frame, render_quality, show_reference
    ):
        exec_script = self._file.execute_render_playblast_script
        exec_script.output_path.set(path)
        exec_script.start_frame.set(start_frame)
        exec_script.end_frame.set(end_frame)
        exec_script.render_quality.set(render_quality)
        exec_script.show_ref.set(show_reference)
        ret = exec_script.run(None)
        self.script_runner = (
            self.root()
            .session()
            .cmds.SubprocessManager.get_runner_info(ret["runner_id"])
        )

    def check_audio(self):
        mng = self.root().project().get_task_manager()
        default_files = mng.default_files.get()
        for file_name, task_names in default_files.items():
            if "animatic.wav" in file_name:
                task = default_files[file_name][0]
                file_mapped_name = file_name.replace(".", "_")
                break

        if not self._shot.tasks.has_mapped_name(task):
            return None
        self.animatic_task = self._shot.tasks[task]

        name, ext = file_mapped_name.split("_")

        if not self.animatic_task.files.has_file(name, ext):
            return None
        f = self.animatic_task.files[file_mapped_name]
        rev = f.get_head_revision()
        rev_path = rev.get_path()

        if os.path.exists(rev_path):
            export_audio = self._file.export_ae_audio
            export_audio._audio_path.set(rev_path)
            return True
        else:
            return False

    def _export_audio(self):
        export_audio = self._file.export_ae_audio
        ret = export_audio.run("Export")
        return ret

    def _mark_image_sequence(self, folder_name, revision_name, render_pid):
        mark_sequence_wait = self._file.mark_image_sequence_wait
        mark_sequence_wait.folder_name.set(folder_name)
        mark_sequence_wait.revision_name.set(revision_name)
        for pid in render_pid:
            mark_sequence_wait.wait_pid(pid)
        mark_sequence_wait.run(None)

    def run(self, button):
        if button == "Cancel":
            return

        rev = self._file.get_revision(self.revision.get())
        self.start_tvpaint(rev.get_path())

        output_name = f"{self._sequence.name()}_{self._shot.name()}.#.png"
        output_path = os.path.join(
            self.ensure_render_folder_revision().get_path(), output_name
        )

        if (
            os.path.exists(os.path.split(output_path)[0])
            and self.keep_existing_frames.get() is False
        ):
            remove_folder_content(os.path.split(output_path)[0])

        self.execute_render_script(
            output_path,
            self.start_frame.get(),
            self.end_frame.get(),
            self.render_quality.get(),
            self.show_reference.get(),
        )
        if not self.check_audio():
            self._export_audio()

        # Configure image sequence marking
        folder_name = self._file.name()[: -len(self._file.format.get())]
        folder_name += "render"
        if self.render_quality.get() == "Preview":
            folder_name += "_preview"
        revision_name = self.revision.get()
        self._mark_image_sequence(
            folder_name,
            revision_name,
            render_pid=[self.tvpaint_runner["pid"], self.script_runner["pid"]],
        )


class ExportAudio(flow.Action):
    _file = flow.Parent()
    _files = flow.Parent(2)
    _task = flow.Parent(3)
    _shot = flow.Parent(5)

    _audio_path = flow.Param("")

    def allow_context(self, context):
        return False

    def get_latest_animatic(self):
        mng = self.root().project().get_task_manager()
        default_files = mng.default_files.get()
        for file_name, task_names in default_files.items():
            if "animatic" in file_name:
                if "wav" in file_name:
                    continue
                task = default_files[file_name][0]
                file_mapped_name = file_name.replace(".", "_")
                break

        if not self._shot.tasks.has_mapped_name(task):
            return None
        self.animatic_task = self._shot.tasks[task]

        name, ext = file_mapped_name.split("_")

        if not self.animatic_task.files.has_file(name, ext):
            return None
        f = self.animatic_task.files[file_mapped_name]

        rev = f.get_head_revision(sync_status="Available")
        return rev if rev is not None else None

    def get_default_file(self):
        mng = self.root().project().get_task_manager()
        default_files = mng.default_files.get()
        for file_name, task_names in default_files.items():
            if "animatic.wav" in file_name:
                task = default_files[file_name][0]
                file_mapped_name = file_name.replace(".", "_")
                break

        dft_task = mng.default_tasks[task]
        if not dft_task.files.has_mapped_name(file_mapped_name):  # check default file
            # print(f'Scene Builder - default task {task_name} has no default file {filename} -> use default template')
            return None

        dft_file = dft_task.files[file_mapped_name]
        return dft_file

    def _ensure_file(self, name, format, path_format, source_revision):
        file_name = "%s_%s" % (name, format)

        if self.animatic_task.files.has_file(name, format):
            f = self.animatic_task.files[file_name]
        else:
            f = self.animatic_task.files.add_file(
                name=name,
                extension=format,
                tracked=True,
                default_path_format=path_format,
            )

        f.file_type.set("Works")

        if f.has_revision(source_revision.name()):
            audio_revision = f.get_revision(source_revision.name())
        else:
            audio_revision = f.add_revision(
                name=source_revision.name(), comment=source_revision.comment.get()
            )

        audio_revision.set_sync_status("Available")

        _audio_path = audio_revision.get_path().replace("\\", "/")

        if not os.path.exists(_audio_path):
            os.makedirs(os.path.dirname(_audio_path), exist_ok=True)
        else:
            os.remove(_audio_path)

        return _audio_path

    def get_audio_path(self):
        return self._audio_path.get()

    def run(self, button):
        if button == "Cancel":
            return

        self._audio_path.set(None)

        # Get latest animatic revision
        animatic_rev = self.get_latest_animatic()
        if animatic_rev:
            animatic_path = animatic_rev.get_path()
            if os.path.isfile(animatic_path):
                # Create audio revision according to animatic number
                path_format = None

                default_file = self.get_default_file()
                if default_file is not None:
                    path_format = default_file.path_format.get()

                    audio_path = self._ensure_file(
                        name="animatic",
                        format="wav",
                        path_format=path_format,
                        source_revision=animatic_rev,
                    )

                    subprocess.call(
                        f"ffmpeg -i {animatic_path} -map 0:a {audio_path} -y",
                        shell=True,
                    )
                    self._audio_path.set(audio_path)
                else:
                    self.root().session().log_error(
                        "[Reload Audio] Animatic sound default file do not exist"
                    )
            else:
                self.root().session().log_error(
                    "[Reload Audio] Animatic latest revision path do not exist"
                )
        else:
            self.root().session().log_error(
                "[Reload Audio] Animatic latest revision not found"
            )


class MarkImageSeqTvPaint(MarkImageSequence):
    def _get_audio_path(self):
        scene_name = re.search(r"(.+?(?=_render))", self._folder.name()).group()
        scene_name += "_tvpp"

        print("scene_name", scene_name)

        if not self._files.has_mapped_name(scene_name):
            print("[GET_AUDIO_PATH] Scene not found")
            return None

        print(
            "get_audio_path", self._files[scene_name].export_ae_audio.get_audio_path()
        )

        return self._files[scene_name].export_ae_audio.get_audio_path()

    def mark_sequence(self, revision_name):
        # Compute playblast prefix
        prefix = self._folder.name()
        if "preview" in prefix:
            prefix = prefix.replace("_render_preview", "")
        else:
            prefix = prefix.replace("_render", "")

        source_revision = self._file.get_revision(revision_name)
        revision = self._ensure_file_revision(
            f"{prefix}_movie_preview"
            if "preview" in self._folder.name()
            else f"{prefix}_movie",
            revision_name,
        )

        # Get revision available
        revision.set_sync_status("Available")

        revision.comment.set(source_revision.comment.get())

        # Get the path of the first image in folder
        img_path = self._get_first_image_path(revision_name)

        file_name = prefix + ".tvpp"

        self._extra_argv = {
            "image_path": img_path,
            "video_output": revision.get_path(),
            "file_name": file_name,
            "audio_file": self._get_audio_path(),
        }

        return super(MarkImageSequence, self).run("Render")


class StartTvPaint(GenericRunAction):
    file_path = flow.Param()

    def allow_context(self, context):
        return context

    def runner_name_and_tags(self):
        return "TvPaint", []

    def target_file_extension(self):
        return "tvpp"

    def extra_argv(self):
        return [self.file_path.get()]


class ExecuteRenderPlayblastScript(GenericRunAction):
    output_path = flow.Param()
    start_frame = flow.IntParam()
    end_frame = flow.IntParam()
    render_quality = flow.Param()
    show_ref = flow.Param()

    def allow_context(self, context):
        return False

    def runner_name_and_tags(self):
        return "PythonRunner", []

    def get_version(self, button):
        return None

    def get_run_label(self):
        return "Render TvPaint Playblast"

    def extra_argv(self):
        current_dir = os.path.split(__file__)[0]
        script_path = os.path.normpath(os.path.join(current_dir, "scripts/render.py"))
        return [
            script_path,
            "--output-path",
            self.output_path.get(),
            "--start-frame",
            self.start_frame.get(),
            "--end-frame",
            self.end_frame.get(),
            "--render-quality",
            self.render_quality.get(),
            "--show-ref",
            self.show_ref.get(),
        ]


class ExportTVPaintLayersJob(FileJob):

    _file = flow.Parent(2)
    revision = flow.Param()

    def get_label(self):
        return 'EXPORT TVPAINT LAYERS JOB'

    def _do_job(self):
        session = self.root().session()

        session.log_info(f"[{self.get_label()}] Start - {self.get_time()}")

        self.root().project().ensure_runners_loaded()

        # Trigger kitsu login
        kitsu_url = self.root().project().admin.kitsu.server_url.get()
        self.root().project().kitsu_api().set_host(f"{kitsu_url}/api")
        kitsu_status = self.root().project().show_login_page()
        if kitsu_status:
            raise Exception(
                "No connection with Kitsu host. Log in to your account in the GUI session."
            )
            return

        revision = self.revision.get()
        export_comp = self._file.export_layers_to_comp
        export_comp.revision.set(revision)

        result = export_comp.run('Render')
        self.wait_runner([result[1]['runner_id']])

        session.log_info(f"[{self.get_label()}] End - {self.get_time()}")


class SubmitTVPaintExportLayersJob(flow.Action):
    
    _file = flow.Parent()
    _task = flow.Parent(3)
    
    pool = flow.Param('default', SiteJobsPoolNames)
    priority = flow.SessionParam(10).ui(editor='int')
    
    revision = flow.Param().ui(hidden=True)
    
    def get_buttons(self):
        self.message.set('<h2>Submit TVPaint export layers to pool</h2>')
        self.pool.apply_preset()
        return ['Submit', 'Cancel']
    
    def allow_context(self, context):
        return False
    
    def _get_job_label(self):
        settings = get_contextual_dict(self._file, "settings")
        file_label = [
            settings['project_name'],
            settings['sequence'],
            settings['shot'],
            settings['task'],
            settings['file_display_name'],
            self.revision.get()
        ]
        label = f"TVPaint Export Layers - {' '.join(file_label)}"
        return label
    
    def run(self, button):
        if button == 'Cancel':
            return

        # Update pool preset
        self.pool.update_preset()

        job = self._file.jobs.create_job(job_type=ExportTVPaintLayersJob)
        job.revision.set(self.revision.get())
        site_name = self.root().project().get_current_site().name()        

        self._task.change_kitsu_status._is_job.set(True)
        self._task.change_kitsu_status._job_type.set("d'export")
        self._task.change_kitsu_status._status.set("ON_HOLD")
        self._task.change_kitsu_status._pool_name.set(self.pool.get())
        self._task.change_kitsu_status.run("run")

        job.submit(
            pool=site_name + '_' + self.pool.get(),
            priority=self.priority.get(),
            label=self._get_job_label(),
            creator=self.root().project().get_user_name(),
            owner=self.root().project().get_user_name(),
            paused=False,
            show_console=False,
        )


class ExportLayersToComp(flow.Action):
    ICON = ("icons.libreflow", "tvpaint")

    _file = flow.Parent()
    _files = flow.Parent(2)
    _task = flow.Parent(3)
    _shot = flow.Parent(5)
    _sequence = flow.Parent(7)

    revision = flow.Param(None, FileRevisionNameChoiceValue)

    def allow_context(self, context):
        return context and self._file.format.get() == "tvpp"

    def get_buttons(self):
        self.revision.revert_to_default()

        buttons = ["Export", "Cancel"]
        if (
            self.root().project().get_current_site().site_type.get() == "Studio"
            and self.root().project().get_current_site().pool_names.get()
        ):
            buttons.insert(1, "Submit job")
        return buttons

    def ensure_layers_folder(self):
        folder_name = "layers"

        task = self._shot.tasks["compositing"]

        if not task.files.has_folder(folder_name):
            task.files.create_folder_action.folder_name.set(folder_name)
            task.files.create_folder_action.category.set("Inputs")
            task.files.create_folder_action.tracked.set(True)
            task.files.create_folder_action.run(None)

        return task.files[folder_name]

    def ensure_layers_folder_revision(self):
        folder = self.ensure_layers_folder()
        revision_name = self.revision.get()
        source_revision = self._file.get_revision(self.revision.get())

        if not folder.has_revision(revision_name):
            revision = folder.add_revision(revision_name)
            folder.set_current_user_on_revision(revision_name)
        else:
            revision = folder.get_revision(revision_name)

        revision.comment.set(source_revision.comment.get())
        revision.set_sync_status("Available")

        folder.ensure_last_revision_oid()

        self._shot.tasks["compositing"].files.touch()

        return revision

    def start_tvpaint(self, path):
        start_action = self._task.start_tvpaint
        start_action.file_path.set(path)
        ret = start_action.run(None)
        self.tvpaint_runner = (
            self.root()
            .session()
            .cmds.SubprocessManager.get_runner_info(ret["runner_id"])
        )

    def execute_render_script(self, path):
        exec_script = self._file.execute_export_layers_script
        exec_script.output_path.set(path)
        ret = exec_script.run(None)
        self.script_runner = (
            self.root()
            .session()
            .cmds.SubprocessManager.get_runner_info(ret["runner_id"])
        )
        return ret

    def run(self, button):
        if button == "Cancel":
            return
        elif button == "Submit job":
            submit_action = self._file.submit_tvpaint_export_layers_job
            submit_action.revision.set(self.revision.get())
            
            return self.get_result(
                next_action=submit_action.oid()
            )
        
        self._task.change_kitsu_status._is_job.set(False)
        self._task.change_kitsu_status._job_type.set("d'export")
        self._task.change_kitsu_status._status.set("Work In Progress")
        self._task.change_kitsu_status.run("run")

        rev = self._file.get_revision(self.revision.get())
        self.start_tvpaint(rev.get_path())

        output_name = f"{self._sequence.name()}_{self._shot.name()}_layers_data.json"
        output_path = os.path.join(
            self.ensure_layers_folder_revision().get_path(), output_name
        )

        if os.path.exists(os.path.split(output_path)[0]):
            remove_folder_content(os.path.split(output_path)[0])

        ret = self.execute_render_script(output_path)

        self._task.kitsu_status_end_process.wait_pid(self.script_runner["pid"])
        wait_dict = self._task.kitsu_status_end_process.run('wait')
        return self.script_runner, wait_dict


class ExecuteExportLayersScript(GenericRunAction):
    output_path = flow.Param()

    def allow_context(self, context):
        return False

    def runner_name_and_tags(self):
        return "PythonRunner", []

    def get_version(self, button):
        return None

    def get_run_label(self):
        return "Export TvPaint Layers"

    def extra_argv(self):
        current_dir = os.path.split(__file__)[0]
        script_path = os.path.normpath(
            os.path.join(current_dir, "scripts/export_layers.py")
        )
        return [script_path, "--output-path", self.output_path.get()]


def start_tvpaint(parent):
    if isinstance(parent, Task):
        r = flow.Child(StartTvPaint)
        r.name = "start_tvpaint"
        r.index = None
        r.ui(hidden=True)
        return r


def export_audio(parent):
    if isinstance(parent, TrackedFile) and (parent.name().endswith("_tvpp")):
        r = flow.Child(ExportAudio)
        r.name = "export_ae_audio"
        r.index = None
        r.ui(hidden=True)
        return r


def render_tvpaint_playblast(parent):
    if isinstance(parent, TrackedFile) and (parent.name().endswith("_tvpp")):
        r = flow.Child(RenderTvPaintPlayblast)
        r.name = "render_tvpaint_playblast"
        r.index = None
        return r


def execute_render_playblast_script(parent):
    if isinstance(parent, TrackedFile) and (parent.name().endswith("_tvpp")):
        r = flow.Child(ExecuteRenderPlayblastScript)
        r.name = "execute_render_playblast_script"
        r.index = None
        r.ui(hidden=True)
        return r


def mark_sequence_tvpaint(parent):
    if isinstance(parent, TrackedFolder):
        r = flow.Child(MarkImageSeqTvPaint)
        r.name = "mark_image_sequence"
        r.index = None
        return r


def export_layers_to_comp(parent):
    if (
        isinstance(parent, TrackedFile)
        and (parent.name().endswith("_tvpp"))
        and parent.root().project().name() == "_2h14"
    ):
        export = flow.Child(ExportLayersToComp)
        export.name = "export_layers_to_comp"
        export.index = None

        submit = flow.Child(SubmitTVPaintExportLayersJob)
        submit.name = "submit_tvpaint_export_layers_job"
        submit.ui(hidden=True)
        return [export, submit]


def execute_export_layers_script(parent):
    if isinstance(parent, TrackedFile) and (
        parent.name().endswith("_tvpp") and parent.root().project().name() == "_2h14"
    ):
        r = flow.Child(ExecuteExportLayersScript)
        r.name = "execute_export_layers_script"
        r.index = None
        r.ui(hidden=True)
        return r


def install_extensions(session):
    return {
        "tvpaint_playblast": [
            start_tvpaint,
            render_tvpaint_playblast,
            execute_render_playblast_script,
            export_audio,
            mark_sequence_tvpaint,
            export_layers_to_comp,
            execute_export_layers_script,
        ]
    }
