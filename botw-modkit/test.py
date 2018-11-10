import sys
import pathlib
import resource

root = resource.RootNode(pathlib.Path(sys.argv[1]))
root.build_all_children(stop_at_sarc=False)

actor = [x for x in root.children if x.name == "Actor"][0]
pack = [x for x in actor.children if x.name == "Pack"][0]
actorpack = [x for x in pack.children if x.name == "ActorObserverByActorTagTag.sbactorpack"][0]
print(actorpack.get_data())