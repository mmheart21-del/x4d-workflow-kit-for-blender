import bpy,sys,os,addon_utils
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
errors=[]
mod=addon_utils.enable('x4d_workflow',default_set=False,handle_error=lambda:errors.append(sys.exc_info()))
assert mod is not None and not errors,errors
assert mod.__addon_enabled__
assert len(mod.icons._preview)==131
assert hasattr(bpy.types.Object,'cw')
addon_utils.disable('x4d_workflow',default_set=False)
assert not hasattr(bpy.types.Object,'cw')
# Explicitly exercise failure rollback, including restricted registration.
from _bpy_restrict_state import RestrictBlend
with RestrictBlend():
    mod.register()
mod.unregister()
original=mod.icons.read_rgba
mod.icons.read_rgba=lambda path:(_ for _ in ()).throw(ValueError('injected icon failure'))
try:
    with RestrictBlend():mod.register()
except ValueError:pass
else:raise AssertionError('Expected icon failure')
assert not mod._registered and mod.icons._preview is None
assert not hasattr(bpy.types.Object,'cw')
mod.icons.read_rgba=original
with RestrictBlend():mod.register()
mod.unregister();mod.unregister()
print('CW_RESTRICTED_ENABLE_OK')
