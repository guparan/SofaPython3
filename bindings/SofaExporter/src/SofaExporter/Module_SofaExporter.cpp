/*********************************************************************
Copyright 2019, CNRS, University of Lille, INRIA

This file is part of sofaPython3

sofaPython3 is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

sofaPython3 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with sofaqtquick. If not, see <http://www.gnu.org/licenses/>.
*********************************************************************/
/********************************************************************
 Contributors:
    - damien.marchal@univ-lille.fr
    - bruno.josue.marques@inria.fr
    - eve.le-guillou@centrale.centralelille.fr
    - jean-nicolas.brunet@inria.fr
    - thierry.gaugry@inria.fr
********************************************************************/

#include <pybind11/eval.h>
namespace py = pybind11;

#include <SofaPython3/Sofa/Core/Binding_Base.h>
#include <SofaPython3/Sofa/Core/Binding_BaseObject.h>

#include <SofaExporter/Binding_STLExporter.h>

namespace sofapython3
{

PYBIND11_MODULE(SofaExporter, m) {
    m.doc() = R"doc(
              Binding for the SofaExporter plugin
              -----------------------------------

              Provides python bindings for the SofaExporter module

              Example of use:

              .. code-block:: python

                import SofaExporter

              .. autosummary::
                  :toctree: _autosummary/_autosummary

                  SofaExporter.STLExporter

              )doc";

    py::module::import("Sofa.Core");

    moduleAddSTLExporter(m);
}

}  // namespace sofapython3

