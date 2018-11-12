import sys
import pathlib
import file_tree

root = file_tree.RootNode(pathlib.Path(sys.argv[1]))
root.build_children_from_fs_recursive()

actor = [x for x in root.get_children() if x.name == "Actor"][0]
pack = [x for x in actor.get_children() if x.name == "Pack"][0]
actorpack = [x for x in pack.get_children() if x.name == "ActorObserverByActorTagTag.sbactorpack"][0]
print(actorpack.wrapper.get_archive().list_files())
actor = [x for x in actorpack.get_children() if x.name == "Actor"][0]
actorlink = [x for x in actor.get_children() if x.name == "ActorLink"][0]
bxml = [x for x in actorlink.get_children() if x.name == "ActorObserverByActorTagTag.bxml"][0]
print(bxml.get_data())