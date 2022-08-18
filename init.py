bl_info = {
    "name": "AnimationKit",
    "author": "JIA ZHIPENG",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Graph Editor > Sidebar > AnimationKit",
    "description": "Tools for applying animation principles",
    "warning": "",
    "doc_url": "",
    "category": "Animation",
}


import bpy
import math
from bpy.types import (Panel, Operator)

################ Math Utils ################
def get_linear_y_value(x1, y1, x2, y2, frame):
    line_slope = (y1 - y2) / (x1 - x2)
    yintercept = (x1 * y2 - x2 * y1) / (x1 - x2)
    value = line_slope * frame + yintercept
    return value

def line_length(pt1, pt2):
    a = pt2[0] - pt1[0]
    b = pt2[1] - pt1[1]
    return math.sqrt(a**2 + b**2)

def get_ease_perc(ease_name, type, perc):
    if type == "IN":
        if ease_name == "SINE":
            return fadeSineConcave(perc) - linear(perc)
        if ease_name == "QUAD":
            return fadeQuadConcave(perc) - linear(perc)
        if ease_name == "CUBIC":
            return fadeCubicConcave(perc) - linear(perc)  
        if ease_name == "QUART":
            return fadeQuartConcave(perc) - linear(perc)
        if ease_name == "EXPO":
            return fadeExpoConcave(perc) - linear(perc)
    if type == "OUT":
        if ease_name == "SINE":
            return fadeSineConvex(perc) - linear(perc)
        if ease_name == "QUAD":
            return fadeQuadConvex(perc) - linear(perc)
        if ease_name == "CUBIC":
            return fadeCubicConvex(perc) - linear(perc)
        if ease_name == "QUART":
            return fadeQuartConvex(perc) - linear(perc)
        if ease_name == "EXPO":
            return fadeExpoConvex(perc) - linear(perc)
    if type == "BOTH":
        if ease_name == "SINE":
            return fadeSineSigmod(perc) - linear(perc)
        if ease_name == "QUAD":
            return fadeQuadSigmod(perc) - linear(perc)
        if ease_name == "CUBIC":
            return fadeCubicSigmod(perc) - linear(perc)
        if ease_name == "QUART":
            return fadeQuartSigmod(perc) - linear(perc)
        if ease_name == "EXPO":
            return fadeExpoSigmod(perc) - linear(perc)


def linear(n):
    return n

# Sinusoidal curve #
def fadeSineConcave(n):
    return -1 * math.cos(n * math.pi / 2) + 1

def fadeSineConvex(n):
    return math.sin(n * math.pi / 2)

def fadeSineSigmod(n):
    return -0.5 * (math.cos(math.pi * n) - 1)

# Quadratic curve #
def fadeQuadConcave(n):
    return n**2

def fadeQuadConvex(n):
    return -n * (n-2)

def fadeQuadSigmod(n):
    if n < 0.5:
        return 2 * n**2
    else:
        n = n * 2 - 1
        return -0.5 * (n*(n-2) - 1)

# Cubic curve #
def fadeCubicConcave(n):
    return n**3

def fadeCubicConvex(n):
    n = n - 1
    return n**3 + 1

def fadeCubicSigmod(n):
    n = 2 * n
    if n < 1:
        return 0.5 * n**3
    else:
        n = n - 2
        return 0.5 * (n**3 + 2)

# Quartic curve #
def fadeQuartConcave(n):
    return n**4

def fadeQuartConvex(n):
    n = n - 1
    return -(n**4 - 1)

def fadeQuartSigmod(n):
    n = 2 * n
    if n < 1:
        return 0.5 * n**4
    else:
        n = n - 2
        return -0.5 * (n**4 - 2)

# Exponetial curve #
def fadeExpoConcave(n):
    if n == 0:
        return 0
    else:
        return 2**(10 * (n - 1))

def fadeExpoConvex(n):
    if n == 1:
        return 1
    else:
        return -(2 ** (-10 * n)) + 1

def fadeExpoSigmod(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        n = n * 2
        if n < 1:
            return 0.5 * 2**(10 * (n - 1))
        else:
            n -= 1
            # 0.5 * (-() + 2)
            return 0.5 * (-1 * (2 ** (-10 * n)) + 2)
############################################


################## Timing ##################
class Timing_Props(bpy.types.PropertyGroup):
                
    mode: bpy.props.EnumProperty(
        name = "Mode",
        default ="SELECTED_FCURVE",
        description = "Selection mode",
        items = [("SELECTED_FCURVE","Selected F-Curves","Exaggerate all frames of selected F-Curves."),
                ("SELECTED_KEYS","Selected Keyframes","Exaggerate selected keyframes.")]
    ) 
    
    def update_prop(self, context):
        scene = context.scene
        fcurves = bpy.context.selected_editable_fcurves[:]

        for fcurve in fcurves:
            offset_sum = 0;            
            for k in fcurve.keyframe_points:
                if self.mode == "SELECTED_KEYS":
                    if k.select_control_point:
                        original_dist = k.co[0] - k.handle_left[0]
                        scale_dist = original_dist * self.amount
                        offset = original_dist - scale_dist
                        offset_sum += offset
                    k.handle_left[0] -= offset_sum
                    k.handle_right[0] -= offset_sum
                    k.co[0] -= offset_sum
                else:
                    k.handle_left[0] *= self.amount
                    k.handle_right[0] *= self.amount
                    k.co[0] *= self.amount
                
    amount: bpy.props.FloatProperty(
        name = "Timing Amount",
        description = "Amount by which to change the timing of selected F-Curves. ",
      #  set = set_track_values,
        update = update_prop,
        default =1.0,
        soft_min = 0.1, soft_max = 10
    )
############################################


########### Slow in and Slow out ###########
class SlowInOut_Props(bpy.types.PropertyGroup):
    type: bpy.props.EnumProperty(
        name= "Type",
        default="OUT",
        description= "Specify the Fade type.",
        items= [
            ("IN","In","Slow keyframes in."),
            ("OUT","Out","Slow keyframes out."),
            ("BOTH","Both","Slow keyframes in and out."),
        ]
    )
    
    mode: bpy.props.EnumProperty(
        name= "Mode",
        default ="SINE",
        description = "Ease function to use for fading.",
        items = [
                ("SINE","Sinusoidal","Fade according to Sinusoidal Curve"),
                ("QUAD","Quadratic","Fade according to Quadratic Curve"),
                ("CUBIC","Cubic","Fade according to Fade according to Cubic Curve"),
                ("QUART","Quartic","Fade according to Quartic Curve"),
                ("EXPO","Expo","Fade according to Exponetial Curve"),
        ]
    )
    
    key: bpy.props.IntProperty(
        name = "Key numbers",
        default = 5,
        description = "Number of keys to slow in/out.",
        soft_min = 0, soft_max = 50
    )
 
    def slowInOut(self,fcurve):
        x1 = fcurve.keyframe_points[0].co[0]
        x2 = fcurve.keyframe_points[-1].co[0]
        y1 = fcurve.keyframe_points[0].co[1]
        y2 = fcurve.keyframe_points[-1].co[1]
        
        if self.amount != 0:
            keyframes = fcurve.keyframe_points[:self.key]
            keyframes.reverse()

            key_values = list(map(lambda x : x.co[1], keyframes))
            maximum = max(key_values)
            minimum = min(key_values)
            
            for i, keyframe in enumerate(keyframes):
                amount = self.amount/10

                x = keyframe.co[0]
                y = keyframe.co[1]
                first = keyframes[0].co
                last = keyframes[-1].co
                
                handle_left_value_offset = keyframe.co[1] - keyframe.handle_left[1]
                handle_right_value_offset = keyframe.co[1] - keyframe.handle_right[1]

                y_target = get_linear_y_value(x1,y1,x2,y2,x)
                distance = line_length(first, last)
                y_dist = line_length(first, [x, y_target])
                perc = 0
                if distance != 0:
                    perc = y_dist / distance

                ease = get_ease_perc(self.mode, self.type, perc) * amount
                ease_perc_y = y - ease
                if ease_perc_y > maximum:
                    ease_perc_y = maximum
                if ease_perc_y < minimum:
                    ease_perc_y = minimuml
                print(ease)
                
                keyframe.co[1] = ease_perc_y
                keyframe.handle_left[1] = ease_perc_y - handle_left_value_offset
                keyframe.handle_right[1] = ease_perc_y - handle_right_value_offset
        
        
    def update_prop(self, context):
        scene = context.scene
        fcurves = bpy.context.selected_editable_fcurves[:]
        for fcurve in fcurves:
            self.slowInOut(fcurve)
 
        
    amount: bpy.props.FloatProperty(
        name = "Slowness Amount",
        description = "Amount by which to slow in/out selected F-Curves. ",
        # set = set_track_values,
        update = update_prop,
        default =1.0,
        soft_min = 0, soft_max = 10
    )
    
############################################


############### Exaggeration ###############
class Exaggeration_Props(bpy.types.PropertyGroup):
    mode: bpy.props.EnumProperty(
        name = "Mode",
        default ="SELECTED_FCURVE",
        description = "Selection mode",
        items = [("SELECTED_FCURVE","Selected F-Curves","Exaggerate all frames of selected F-Curves."),
                ("SELECTED_KEYS","Selected Keyframes","Exaggerate selected keyframes.")]
    )
    
    base: bpy.props.EnumProperty(
        name= "Base",
        description= "Repeating mode to use before the first keyframe",
        default="CENTER",
        items= [
            ("CENTER","Center","Exaggerate keys from the selection's center point."),
            ("FIRST","First","Exaggerate keys from the selection's first point."),
            ("MAX","Max","Exaggerate keys from the selection's keyframe with maximum value."),
            ("MIN","Min","Exaggerate keys from the selection's keyframe with minimum value."),
            ("NONE","None","Exaggerate keys from the selection's keyframe."),
        ]
    )
 
 
    def get_bounding_box(self,fcurve):
        points = list()
        if self.mode == "SELECTED_KEYS":
            points = [x for x in fcurve.keyframe_points if x.select_control_point == True]
            if len(points) == 0:
                return None
        elif self.base == "FIRST":
            for x in fcurve.keyframe_points:
                if x.select_control_point == True:
                    points = [x]
                    break
            if len(points) == 0:
                points = fcurve.keyframe_points
        else:
            points = fcurve.keyframe_points
        key_values = list(map(lambda x : x.co[1], points))
        maximum = max(key_values)
        minimum = min(key_values)

        if self.base == "CENTER":
            return (maximum+minimum)/2
        elif self.base == "FIRST":
            return key_values[0]
        elif self.base == "MAX":
            return maximum
        elif self.base == "MIN":
            return minimum
        return None

    def amplifyWithBase(self,pivot,k):
        key_distance = pivot - k.co[1]
        hl_distance = pivot - k.handle_left[1]
        hr_distance = pivot - k.handle_right[1]
        k.co[1] = pivot - (key_distance * self.amount)
        k.handle_left[1] = pivot - (hl_distance * self.amount)
        k.handle_right[1] = pivot - (hr_distance * self.amount)

    def amplify(self,pivot,k):
        k.co[1] = k.co[1] * self.amount
        k.handle_left[1] = k.handle_left[1] * self.amount
        k.handle_right[1] = k.handle_right[1] * self.amount

    def update_prop(self, context):
        print("update")
        print(self.amount)
        print(self.base)
        
        scene = context.scene
        fcurves = bpy.context.selected_editable_fcurves[:]

        for fcurve in fcurves:
            pivot = self.get_bounding_box(fcurve)
            print("pivot")
            print(pivot)
            if pivot != None:
                for k in fcurve.keyframe_points:
                    if self.mode == "SELECTED_KEYS":
                        if k.select_control_point:
                           self.amplifyWithBase(pivot,k)
                    else:
                       self.amplifyWithBase(pivot,k)
            else:
                if self.base == "NONE":
                    for k in fcurve.keyframe_points:
                        if self.mode == "SELECTED_KEYS":
                            if k.select_control_point:
                                self.amplify(pivot,k)
                        else:
                           self.amplify(pivot,k)
    amount: bpy.props.FloatProperty(
        name = "Exaggeration Amount",
        description = "Amount by which to exaggerate selected F-Curves. ",
      #  set = set_track_values,
        update = update_prop,
        default =1.0,
        soft_min = -10, soft_max = 10
    )
    
############################################    


class GRAPH_PT_Timing_Panel(Panel):
    bl_label = "Timing"
    bl_category = "AnimationKit"
    bl_idname = "Animmation_Timing_Panel"
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "scene"

    def draw_header(self, context):
        self.layout.label(text="", icon="EVENT_S")
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        col = layout.column(align=True)
        col.prop(scene.timing_Props, 'mode')
        col.prop(scene.timing_Props, 'amount')
        

class GRAPH_PT_SlowInOut_Panel(Panel):
    bl_label = "Slow in and slow out"
    bl_category = "AnimationKit"
    bl_idname = "Animmation_SlowInOut_Panel"
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "scene"

    def draw_header(self, context):
        self.layout.label(text="", icon="EVENT_S")
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        col = layout.column(align=True)
        col.prop(scene.slowInOut_Props, 'type')
        col.prop(scene.slowInOut_Props, 'mode')
        col.prop(scene.slowInOut_Props, 'key')
        col.prop(scene.slowInOut_Props, 'amount')


class GRAPH_PT_Exaggeration_Panel(Panel):
    bl_label = "Exaggeration"
    bl_category = "AnimationKit"
    bl_idname = "Animmation_Exaggeration_Panel"
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "scene"

    def draw_header(self, context):
        self.layout.label(text="", icon="EVENT_E")
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        col = layout.column(align=True)
        col.prop(scene.exaggeration_props, 'mode')
        col.prop(scene.exaggeration_props, 'base')
        col.prop(scene.exaggeration_props, 'amount')


classes = (
    Timing_Props,
    SlowInOut_Props,
    Exaggeration_Props,
    GRAPH_PT_Timing_Panel,
    GRAPH_PT_SlowInOut_Panel,
    GRAPH_PT_Exaggeration_Panel
)

# Registration
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.timing_Props = bpy.props.PointerProperty(type = Timing_Props)
    bpy.types.Scene.exaggeration_props = bpy.props.PointerProperty(type = Exaggeration_Props)
    bpy.types.Scene.slowInOut_Props = bpy.props.PointerProperty(type = SlowInOut_Props)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
