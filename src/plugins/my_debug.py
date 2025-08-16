import sys
import os
import inspect
import pcbnew
from pcbnew import ToMM, FromMM
from math import floor

__enabled = {}

def dbprint(*args):
    msg = " ".join([str(x) for x in args])
    print(msg)

def debug(*args):
    frame = sys._getframe(1)
    if frame.f_code.co_name == 'debugObj':
        frame = sys._getframe(2)

    filename = os.path.basename(frame.f_code.co_filename)

    if __enabled.get(filename, False):
        print("{0}:{1}:{2}: {3}".format(filename, frame.f_lineno, frame.f_code.co_name, "\r\n".join([str(x) for x in args])))

def stringify(obj):
    if isinstance(obj, pcbnew.PCB_SHAPE):
        if obj.ShowShape() == "Line":
            return "Shape.Line.[{0},{1}] - [{2},{3}]".format(ToMM(obj.GetStartX()), ToMM(obj.GetStartY()), ToMM(obj.GetEndX()), ToMM(obj.GetEndY()))
        elif obj.ShowShape() == "Arc":
            angle = floor(obj.GetLength() / obj.GetRadius() * 18000 / 3.1415926535897932384626 + 0.5) / 100
            return "Shape.Arc.[{0},{1}] - [{2},{3}] r={4}, a={5}".format(ToMM(obj.GetStartX()), ToMM(obj.GetStartY()), ToMM(obj.GetEndX()), ToMM(obj.GetEndY()), ToMM(obj.GetRadius()), angle)
    elif isinstance(obj, pcbnew.FOOTPRINT):
        pads = obj.Pads()
        return "Footprint:{0}({1}) [{2},{3}] ({4})".format(obj.GetFPIDAsString(), obj.GetValue(), ToMM(obj.GetPosition()[0]), ToMM(obj.GetPosition()[1]), stringify(pads))
    elif isinstance(obj, pcbnew.PCB_ARC):
        length = obj.GetLength()
        radius = obj.GetRadius()
        angle = floor(length / radius * 18000 / 3.1415926535897932384626 + 0.5) / 100
        return "PCB_ARC.[{0},{1}] - [{2},{3}] l={4}, w={5}, r={6}, a={7}, m={8}".format(ToMM(obj.GetStart()[0]), ToMM(obj.GetStart()[1]), ToMM(obj.GetEnd()[0]), ToMM(obj.GetEnd()[1]), ToMM(length), ToMM(obj.GetWidth()), ToMM(radius), angle, obj.m_Uuid)
    elif isinstance(obj, pcbnew.PCB_TRACK):
        return "PCB_TRACK.[{0},{1}] - [{2},{3}] l={4}, w={5}".format(ToMM(obj.GetStart()[0]), ToMM(obj.GetStart()[1]), ToMM(obj.GetEnd()[0]), ToMM(obj.GetEnd()[1]), ToMM(obj.GetLength()), ToMM(obj.GetWidth()))
    elif isinstance(obj, pcbnew.PAD):
        return "Pad: [{0},{1}] br={2}".format(ToMM(obj.GetPosition()[0]), ToMM(obj.GetPosition()[1]), ToMM(obj.GetBoundingRadius()))
    elif hasattr(obj, "__iter__"):
        return "[" + ", ".join([ (stringify(item) if item != obj else "<<self>>") for item in obj ]) + "]"
    elif isinstance(obj, pcbnew.PCB_TEXT):
        return "Text.[{0},{1}] - '{2}'".format(ToMM(obj.GetPosition()[0]), ToMM(obj.GetPosition()[1]), obj.GetShownText())

    return str(obj)

def debugObj(name, obj):
    msg = "{0} <{1}>".format(name, obj.__class__.__name__)

    for member in inspect.getmembers(obj):
        if not (member[0].startswith('_') or inspect.ismethod(member[1]) or inspect.isfunction(member[1])):
            msg = "{0}\r\n{1} = {2}".format(msg, str(member[0]), stringify(member[1]))

    debug(msg)

def enable_debug(flag=True):
    global __enabled
    frame = sys._getframe(1)
    if frame.f_code.co_name == 'debugObj':
        frame = sys._getframe(2)

    filename = os.path.basename(frame.f_code.co_filename)

    __enabled[filename] = flag

def is_debug_enabled():
    global __enabled
    return __enabled

