import bimpy
import os
import sys
import json
import shutil

ctx = bimpy.Context()

ctx.init(1100, 600, "Edit Configuration")

# data model

class WFile:                        # background / triggered static events /  person sounds
    def __init__(self):
        self.filenames = [""]       # at least 1 or list for random-switched
        self.fade_in = 0
        self.xfade = 0
        self.trigger_name = ""
        self.states = [] # int
        self.loop = True
        self.toggle = False

    def to_dict(self):
        ret = {}
        ret["filenames"] = self.filenames
        ret["fade_in"] = self.fade_in
        ret["xfade"] = self.xfade
        ret["trigger_name"] = self.trigger_name
        ret["states"] = self.states
        ret["loop"] = int(self.loop)
        ret["toggle"] = int(self.toggle)
        return ret

    def from_dict(src):
        ret = WFile()
        ret.filenames = src["filenames"]
        ret.fade_in = src["fade_in"]
        ret.xfade = src["xfade"]
        ret.trigger_name = src["trigger_name"]
        ret.states = src["states"]
        ret.loop = (src["loop"]==1)
        ret.toggle = (src["toggle"]==1)
        return ret

class WConfiguration:
    def __init__(self):
        self.files = [WFile()]                     # WFile

    def to_dict(self):
        ret = {"files" : [x.to_dict() for x in self.files]}
        return ret

    def from_dict(src):
        ret = WConfiguration()
        ret.files = [WFile.from_dict(x) for x in src["files"]]
        return ret

###

# view state

class ViewData:
    local_path = os.path.dirname(os.path.realpath(__file__))
    edit_files = []

    browse_files = None
    browse_path = ""
    selected_filename = ""
    browse_index = None

    selected_configuration = ""
    cfg_to_create = bimpy.String()
    cfg = WConfiguration()

    def media_path():
        return ViewData.local_path + "/media"

    def media_groups():
        ret = []
        for r, d, f in os.walk(ViewData.media_path()):
            ret += d
        return ret

    def full_group_path(grp_name):
        return ViewData.local_path + "/media/" + grp_name


###

# views

def editor_config():
    if (ViewData.selected_configuration==""):
        return

    obj = ViewData.cfg

    bimpy.begin("Configuration")

    bimpy.text("Files: {}".format(len(obj.files)))
    for e, idx in zip(obj.files, range(len(obj.files))):
        sel = bimpy.Bool(e in ViewData.edit_files)
        flags_str = ""
        flags_str += " Toggle" if e.toggle else ""
        flags_str += " Loop" if e.loop else ""
        str_info = """{}: Trigger: '{}'({}) {} Audio files({}): {}""".format(idx,e.trigger_name,str(e.states),flags_str, len(e.filenames), ",".join(["'"+x+"'" for x in e.filenames]))
        if bimpy.checkbox(str_info, sel):
            if sel.value:
                ViewData.edit_files += [e]
            else:
                try:
                    ViewData.edit_files.remove(e)
                except:
                    pass

        if e in ViewData.edit_files:
            editor_file(e)

    if (bimpy.button("Add")):
        obj.files += [WFile()]

    bimpy.separator()

def editor_actions(obj: WFile):
    bimpy.separator()

    bimpy.text("Actions (Gromozeka): ")
    bimpy.text(str(obj.states))
    v1 = bimpy.Bool(1 in obj.states)
    if bimpy.checkbox("Transition to On (1)",v1):
        if (v1.value):
            obj.states += [1]
        else:
            obj.states.remove(1)
    v1 = bimpy.Bool(2 in obj.states)
    if bimpy.checkbox("On (2)",v1):
        if (v1.value):
            obj.states += [2]
        else:
            obj.states.remove(2)
    v1 = bimpy.Bool(3 in obj.states)
    if bimpy.checkbox("Transition to Off (3)",v1):
        if (v1.value):
            obj.states += [3]
        else:
            obj.states.remove(3)
    v1 = bimpy.Bool(4 in obj.states)
    if bimpy.checkbox("Hover (4)",v1):
        if (v1.value):
            obj.states += [4]
        else:
            obj.states.remove(4)

    v1 = bimpy.Bool(5 in obj.states)
    if bimpy.checkbox("Exit Hover (5)",v1):
        if (v1.value):
            obj.states += [5]
        else:
            obj.states.remove(5)

def editor_file(obj: WFile):
    bimpy.begin("File ##" + str(id(obj)))


    for f,idx in zip(obj.filenames, range(len(obj.filenames))):
        bimpy.columns(3)
        bimpy.text("{}:{}".format(idx,f))
        bimpy.next_column()
        if bimpy.button("replace##"+str(id(f))):
            ViewData.browse_index = idx
            ViewData.browse_files = obj
        bimpy.next_column()
        if len(obj.filenames)>1:
            if bimpy.button("del##"+str(id(f))):
                obj.filenames.remove(f)
                break
        else:
            bimpy.text("")
        bimpy.columns(1)
        bimpy.separator()

    bimpy.columns(1)

    sel = bimpy.Bool(ViewData.browse_files != None)
    if bimpy.button("Add file##addfile"):
        sel.value = not sel.value
        if sel.value:
            ViewData.browse_files = obj
        else:
            try:
                ViewData.browse_files = None
            except:
                pass

    if ViewData.browse_files:
        file_browser(obj)

    bimpy.separator()

#    fi = bimpy.Float(obj.fade_in)
#    if bimpy.drag_float("Fade in",fi,.5,0,60):
#        obj.fade_in = fi.value

    fi = bimpy.Float(obj.xfade)
    if bimpy.drag_float("Crossfade",fi,.5,0,60):
        obj.xfade = fi.value

    lp = bimpy.Bool(obj.loop)
    if bimpy.checkbox("Loop", lp):
        obj.loop = lp.value

    lp = bimpy.Bool(obj.toggle)
    if bimpy.checkbox("Toggle", lp):
        obj.toggle = lp.value

    editor_actions(obj)

    bimpy.separator()

    s1 = bimpy.String(obj.trigger_name)
    if bimpy.input_text("Trigger",s1, 128):
        obj.trigger_name = s1.value

#    bimpy.input_text("Coordinate", s1, 128)

#    bimpy.separator()
#    editor_channelmap_inline(obj.channelmap)

    bimpy.end()

import os
import platform
import subprocess

def open_file(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])

def _file_ok_button(obj, name :str):
    if ViewData.selected_filename != "":
        if bimpy.button("OK##"+str(name)):
            if ViewData.browse_index!=None:
                obj.filenames[ViewData.browse_index] = ViewData.selected_filename
            else:
                obj.filenames += [ViewData.selected_filename]
            ViewData.browse_files = None
            ViewData.browse_index = None
            ViewData.selected_filename = ""
        bimpy.same_line()
def _file_browser_ok_cancel_buttons(obj):
    _file_ok_button(obj,"")

    if bimpy.button("Cancel"):
        ViewData.browse_files = None
        ViewData.selected_filename = ""

def file_browser(obj):
    bimpy.begin("File browser")
    bimpy.text("Group:")
    bimpy.separator()
    bimpy.columns(2)
    for x in ViewData.media_groups():
        bs = bimpy.Bool(x in ViewData.browse_path)
        if bimpy.selectable(x, bs):
            ViewData.browse_path = x
        bimpy.next_column()

        if bimpy.button("Open location##"+x):
            open_file(ViewData.full_group_path(x))
        bimpy.next_column()

    bimpy.columns(1)

    bimpy.text("Selected: '"+ViewData.selected_filename+"'")
    bimpy.separator()

    bimpy.text("Files:")

    _file_browser_ok_cancel_buttons(obj)
    
    bimpy.separator()

    if ViewData.browse_path != "":
        files = []
        for r, d, f in os.walk(ViewData.full_group_path(ViewData.browse_path)):
            for file in f:
                files.append(os.path.join(r, file))
                sel = bimpy.Bool(os.path.basename(ViewData.selected_filename) == os.path.basename(files[-1]) ) #files[-1])
                
                if (sel.value):
                    _file_ok_button(obj,os.path.basename(files[-1]))
                if bimpy.selectable(os.path.basename(files[-1]), sel):
                    ViewData.selected_filename = ViewData.browse_path+"/"+ os.path.basename(files[-1])

    bimpy.separator()

    bimpy.text("")

    bimpy.end()

def config_browser():
    bimpy.begin("Config File")

    if ViewData.selected_configuration == "":
        files = []
        for r, d, f in os.walk(ViewData.local_path):
            for file in f:
                if file.endswith('.json') and not file.endswith('.bk.json'):
                    files.append(os.path.join(r, file))
                    sel = bimpy.Bool(ViewData.selected_configuration == files[-1])
                    if bimpy.selectable(os.path.basename(files[-1]), sel):
                        ViewData.selected_configuration = files[-1]
                        f = open(ViewData.selected_configuration)
                        print(ViewData.selected_configuration)
                        js = json.load(f)
                        ViewData.cfg = WConfiguration.from_dict(js)
                        print(js)
                        f.close()
        bimpy.separator()

        bimpy.text("Add new config:")
        bimpy.input_text("##newcfg_txt",  ViewData.cfg_to_create, 32)

        bimpy.same_line()
        if bimpy.button("Add##newcfg"):
            if ViewData.cfg_to_create!="":
                f = open(ViewData.local_path + "/"+ ViewData.cfg_to_create.value + ".json","w")
                f.write(json.dumps(WConfiguration().to_dict(), indent = 4))
                f.close()
                ViewData.cfg_to_create.value = ""

        bimpy.separator()
        if bimpy.button("Open location"):
            open_file(ViewData.local_path)

        bimpy.end()
    else:
        bimpy.text("Editing: "+ os.path.basename(ViewData.selected_configuration))

        bimpy.separator()

        if bimpy.button("Save file"):
            dest = ViewData.selected_configuration.replace(".json",".bk.json")
            shutil.copyfile( ViewData.selected_configuration,dest)

            f = open(ViewData.selected_configuration,"w")
            f.write(json.dumps(ViewData.cfg.to_dict(), indent = 4))
            f.close()

        bimpy.separator()
        if bimpy.button("Close file"):
            ViewData.selected_configuration = ""


###
# main
while(not ctx.should_close()):
        with ctx:
            config_browser()
            editor_config()

