import sys
import pathlib
import resource

dump_workspace_path = pathlib.Path(sys.argv[1])
my_res_path = pathlib.Path("Actor", "Pack", "ActorObserverByActorTagTag.sbactorpack",)

workspace_manager = resource.WorkspaceManager(dump_workspace_path)
dump_workspace = workspace_manager.dump_workspace
print([x.name for x in dump_workspace.top_dir_res.contents])