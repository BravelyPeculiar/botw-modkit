import sys
import pathlib
import botw_resource

dump_root_path = pathlib.Path(sys.argv[1])
my_rel_path = pathlib.Path("Actor", "Pack", "ActorObserverByActorTagTag.sbactorpack", "Actor", "ActorLink", "ActorObserverByActorTagTag.bxml")

resource_manager = botw_resource.BotwResourceManager(dump_root_path)
resource = resource_manager.get_resource(dump_root_path, my_rel_path)
my_data = resource.get_data()
print(my_data)