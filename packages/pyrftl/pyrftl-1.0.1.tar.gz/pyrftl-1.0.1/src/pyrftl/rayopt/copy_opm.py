from rayoptics.elem.elements import Assembly
from rayoptics.elem import parttree
from rayoptics.raytr import trace as trace
from math import sqrt

from copy import deepcopy  # to copy an object

# function copy_opm_internal is a fork of ele.create_from_file from ray-optics v0.8.7 from Michael J Hayford
# https://github.com/mjhoptics/ray-optics/blob/9ee2b7fdc0bfd81bb7658d3589b21a33398dc940/src/rayoptics/elem/elements.py#L276
# original function is under the following licence
# As only minor changes were done, only the original licence should be considered if it is reused
#
# BSD 3-Clause License
#
# Copyright (c) 2017-2024, Michael J. Hayford
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


def copy_opm_internal(opm_to_copy, **kwargs):  # modified line 1/2
    # fork of function ele.create_from_file from ray-optics v0.9.1 from Michael J Hayford <mjhoptics@gmail.com>
    # this function is intended to be a factory_fct to be use to copy elements of an optical model into
    # another one (so not obj, img or wvl etc, just surfaces)

    opm_file = deepcopy(opm_to_copy)  # modified line 2/2
    # if not deepcopy, the "copied" opm sequence is still linked to the opm to copied,
    # so when one is changed the other is affected !

    sm_file = opm_file['seq_model']
    osp_file = opm_file['optical_spec']
    pm_file = opm_file['parax_model']
    em_file = opm_file['ele_model']
    pt_file = opm_file['part_tree']
    ar_file = opm_file['analysis_results']
    if len(pt_file.nodes_with_tag(tag='#element')) == 0:
        parttree.sequence_to_elements(sm_file, em_file, pt_file)

    if 'power' in kwargs:
        desired_power = kwargs['power']
        cur_power = ar_file['parax_data'].fod.power
        # scale_factor is linear, power is 1/linear
        #  so use reciprocal of power to compute scale_factor
        scale_factor = cur_power / desired_power
        opm_file.apply_scale_factor(scale_factor)

    # extract the system definition, minus object and image
    seq = [list(node) for node in sm_file.path(start=1, stop=-1)]
    seq[-1][1] = None

    if 'prx' in kwargs:
        dgm = pm_file.match_pupil_and_conj(kwargs['prx'])
    else:
        dgm = None

    # get the top level nodes of the input system, minus object and image
    part_nodes = pt_file.nodes_with_tag(tag='#element#airgap#assembly',
                                        not_tag='#object#image',
                                        node_list=pt_file.root_node.children)
    parts = [part_node.id for part_node in part_nodes]

    if len(part_nodes) == 1 and '#assembly' in part_nodes[0].tag:
        asm_node = part_nodes[0]
        print("found root assembly node")
    else:
        # create an Assembly from the top level part list
        label = kwargs.get('label', None)
        tfrm = kwargs.get('tfrm', opm_file['seq_model'].gbl_tfrms[1])
        asm = Assembly(parts, idx=1, label=label, tfrm=tfrm)
        asm_node = asm.tree(part_tree=opm_file['part_tree'], tag='#file')
    asm_node.parent = None

    return seq, parts, part_nodes, dgm


def set_clear_apertures(sm, avoid_list=None):
    # this function is a fork of seq.sequential.set_clear_apertures from ray-optics v0.9.1 from Michael J Hayford
    # its original goal is to recalculate lens apertures. Here the possibility to not modify some surfaces is added.
    # Thus, it is possible to determine the correct semi diameter of some surfaces, without changing the semi diameter
    # of others. (For example, I do not want to change the semi diameter of the lens I designed, but I need to put the
    # correct semi diameter for obj/img in order to have an optimal view of the wavefront with eval_wavefront function,
    # note that if the vignetting is still wrong, it is probably due a wrong position of the stop surface).
    #
    # input :
    # sm : a rayoptics sequential model
    # avoid_list : list of surfaces indices to not modify (example: [2,3,4,7,8])

    if avoid_list is None:
        avoid_list = []

    rayset = trace.trace_boundary_rays(sm.opt_model, use_named_tuples=True)

    for i, s in enumerate(sm.ifcs):
        if i not in avoid_list :
            max_ap = -1.0e+10
            update = True
            for f in rayset:
                for p in f:
                    ray = p.ray
                    if len(ray) > i:
                        ap = sqrt(ray[i].p[0]**2 + ray[i].p[1]**2)
                        if ap > max_ap:
                            max_ap = ap
                    else:  # ray failed before this interface, don't update
                        update = False
            if update:
                s.set_max_aperture(max_ap)

