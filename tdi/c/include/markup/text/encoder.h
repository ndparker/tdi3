/*
 * Copyright 2013 - 2023
 * Andr\xe9 Malo or his licensors, as applicable
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef TDI_MARKUP_TEXT_ENCODER_H
#define TDI_MARKUP_TEXT_ENCODER_H


#include "cext.h"

extern EXT_LOCAL PyTypeObject TDI_TextEncoder;

#define TDI_TextEncoder_Check(op) \
    PyObject_TypeCheck(op, &TDI_TextEncoder)

#define TDI_TextEncoder_CheckExact(op) \
    ((op)->ob_type == &TDI_TextEncoder)


#endif
