### Features of NGroups
1. Non destructive normal editing.
2. Data stored in blend file.
3. Spherize normals tool.
4. Visual representation of Layers.
5. Mirror support.

## Compute update
Unassigned loop (factor == 0) normal will not be overridden
If you need override, assign to empty vector layer

## Angle counts in counterclockwise direction around Z axis

### How to use?
1. Select mesh object and go to edit mode, NGroups panel should appear.
2. Press "Create NGroups" button.
3. Under the "Layers" tab press plus sign button to add layer.
4. Select vertices or faces and press "Assign" button.

![](https://github.com/Mojuko/NGroups/blob/Gifs/HowToUse.gif)

### Selection dependency
- By assigning/removing vertex, all its linked loops (face corners) will be assigned.
- By assigning/removing face, all face loops (corners) will be assigned, this creates split normals on edges.
- To assign separate loop (face corner) combine selection modes with assign/remove.

![](https://github.com/Mojuko/NGroups/blob/Gifs/SelectionDependency.gif)

### Data computation and mesh operations
- "Apply mesh normals" This button used to apply normals to mesh. This normals will be NOT removed by remove data.
- When NGroups created mesh normals will be automatically stored as base layer to change it use "Apply mesh normals".
- "Remove NGroups data" used to remove all data that stored in mesh.

![](https://github.com/Mojuko/NGroups/blob/Gifs/DataRemoveAndApply.gif)

- Not all actions automatically update data, to perform update press "Compute result".
- "Update mesh normals" used to set mesh normals based on computed result. This normals will be removed if not applied to mesh.

![](https://github.com/Mojuko/NGroups/blob/Gifs/DataUpdate.gif)

### Layers visualization
- To enable visual display, press "Toggle layers display" and set shading mode to "Material Preview". Materials used by mesh will be reverted back, once visualization will be toggled.
- "Show current layer" display raw layer data that updates real-time by any action.
- "Show all layers" display final result of layers blending.

![](https://github.com/Mojuko/NGroups/blob/Gifs/LayersVisualization.gif)

### Layers blending and smooth tools
- To set blending weight for selected loops, use "Corner weight" value and press "Assign". Blending use saved normals, that was stored, when NGroups was applied to mesh button "Apply mesh normals" pressed.
- Layer order matters.
- Blending use slerp for final vectors and lerp for color display.
- "Smooth Brush" (To change size press "F" keyboard button) and "Smooth selection" computes average weight from neighbor vertices.

![](https://github.com/Mojuko/NGroups/blob/Gifs/BlendingAndSmooth.gif)

### Vector layers

1. Set layer type to vector by pressing "V" button.
2. Create vector data by pressing plus sign button.
3. Press "Set vector shape" used to set vector type.
4. Assign vertices or faces to vector and layer weight.
5. Press "Edit selected vector data" to set vector transform.
6. Apply vector.
7. Press "Compute result" to update data.

Vector from same normal layer, will override other vector, if assigned to the same loops (corners).

![](https://github.com/Mojuko/NGroups/blob/Gifs/Vector.gif)

### Mirror
- Before using mirror for layers press "Compute mirrors".
- Mesh change will require mirror computation once again.
- Mirror might cause errors.

![](https://github.com/Mojuko/NGroups/blob/Gifs/Mirror.gif)
