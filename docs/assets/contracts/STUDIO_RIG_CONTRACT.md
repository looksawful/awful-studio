# Studio Rig Contract

`SUPPORT → FIXTURE → MODIFIER` are separate replaceable layers. One fixture may accept multiple compatible modifiers without duplicating the support or pose.

Required semantic points: `MOUNT_SUPPORT`, `MOUNT_FIXTURE`, `MOUNT_MODIFIER`, `MOUNT_UMBRELLA`, `EMITTER_ORIGIN`, `LIGHT_TARGET`, `FLOOR_CONTACT` as applicable.

Configurator changes preserve unrelated state: replacing a Magnum with an Octa does not move the stand or alter native light power. Physical support, grip and modifiers remain ordinary editable Blender objects.
