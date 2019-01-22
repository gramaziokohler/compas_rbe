from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
import compas_rbe

from compas_rhino.utilities import XFunc

from compas_rbe.datastructures import Assembly
from compas_rbe.rhino import AssemblyArtist


# replace this by RPC server
identify_interfaces_ = XFunc('compas_rbe.interfaces.identify_interfaces_xfunc', tmpdir=compas_rbe.TEMP)
compute_iforces_ = XFunc('compas_rbe.equilibrium.compute_iforces_xfunc', tmpdir=compas_rbe.TEMP)

# replace this by automated search for python executables
# based on .(bash_)profile
identify_interfaces_.python = '/Users/vanmelet/anaconda3/bin/python3'
compute_iforces_.python = '/Users/vanmelet/anaconda3/bin/python3'

# replace 
identify_interfaces_.paths = ['/Users/vanmelet/Code/BlockResearchGroup/compas_rbe/src']
compute_iforces_.paths = ['/Users/vanmelet/Code/BlockResearchGroup/compas_rbe/src']


# wrapper
def identify_interfaces(assembly, nmax=10, tmax=0.05, amin=0.01, lmin=0.01):
    data = {'assembly': assembly.to_data(),
            'blocks'  : {str(key): assembly.blocks[key].to_data() for key in assembly.blocks}}
    result = identify_interfaces_(data, nmax=nmax, tmax=tmax, amin=amin, lmin=lmin)
    assembly.data = result['assembly']
    for key in assembly.blocks:
        assembly.blocks[key].data = result['blocks'][str(key)]


#wrapper
def compute_iforces(assembly, solver='CPLEX'):
    data = {'assembly': assembly.to_data(),
            'blocks'  : {str(key): assembly.blocks[key].to_data() for key in assembly.blocks},}
    result = compute_iforces_(data, solver=solver)
    assembly.data = result['assembly']
    for key in assembly.blocks:
        assembly.blocks[key].data = result['blocks'][str(key)]


# initialize assembly and blocks from json file
assembly = Assembly.from_json(compas_rbe.get('simple_stack_1.json'))

# identify block interfaces and update block_model
identify_interfaces(assembly)

# equilibrium
compute_iforces(assembly)

# result
artist = AssemblyArtist(assembly, layer='RBE')
artist.clear_layer()
artist.draw_blocks()
artist.draw_interfaces()
artist.draw_selfweight(scale=0.25)
artist.draw_forces(scale=0.25)
artist.redraw()

# check
total_selfweight = sum(assembly.blocks[key].volume() for key in assembly.vertices_where({'is_support': True}))
total_support = 0

# for a, b, attr in assembly.edges(True):
#     if assembly.vertex[a]['is_support']:
#         for i in range(len(attr['interface_points'])):
#             c_np = attr['interface_forces'][i]['c_np']
#             total_support += c_np
#     elif assembly.vertex[b]['is_support']:
#         for i in range(len(attr['interface_points'])):
#             c_np = attr['interface_forces'][i]['c_np']
#             total_support += c_np
#     else:
#         pass

print(total_support)
print(total_selfweight)