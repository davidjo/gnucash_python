/* -*- Mode: C; c-basic-offset: 4 -*-
 * pyglib - Python bindings for GLIB.
 * Copyright (C) 2007  Gian Mario Tagliaretti
 *
 *   pygkeyfile.c: GKeyFile wrapper.
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
 * USA
 */

#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include <Python.h>

#include <glib.h>

//extern PyTypeObject PyGKeyFile_Type;

typedef struct {
        PyObject_HEAD
        GKeyFile        *key_file;
} PyGKeyFile;

extern PyObject *pygkeyfile_new(GKeyFile *keyfile);

