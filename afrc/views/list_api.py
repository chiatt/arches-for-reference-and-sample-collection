"""
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import logging
from django.views.generic import View
from arches_controlled_lists.models import List, ListItem
from arches.app.utils.response import JSONErrorResponse, JSONResponse
from arches.app.utils.string_utils import str_to_bool
from arches.app.utils.permission_backend import get_nodegroups_by_perm
from arches_controlled_lists.views import _prefetch_terms
from django.utils.translation import gettext as _
from http import HTTPStatus
from arches.app.utils.response import JSONResponse

logger = logging.getLogger(__name__)

class ListAPI(View):
    def get(self, request, list_id):
        """Returns either a flat representation (?flat=true) or a tree (default)."""
        try:
            lst = List.objects.prefetch_related(*_prefetch_terms(request)).get(
                pk=list_id
            )
        except List.DoesNotExist:
            return JSONErrorResponse(status=HTTPStatus.NOT_FOUND)

        flat = str_to_bool(request.GET.get("flat", "false"))
        permitted = get_nodegroups_by_perm(request.user, "read_nodegroup")
        serialized = lst.serialize(flat=flat, permitted_nodegroups=permitted)

        return JSONResponse(serialized)
    
class ListItemAPI(View):
    def get(self, request, item_id):
        """Returns either a flat representation (?flat=true) or a tree (default)."""
        try:
            item = ListItem.objects.filter(pk=item_id).first()
            children = item.children.all()
            parent = item.parent
            payload = {
                "item": item,
                "children": children,
                "parent": parent,
                "grandparent": parent.parent,
            }
        except (ListItem.DoesNotExist, AttributeError):
            return JSONErrorResponse(status=HTTPStatus.NOT_FOUND)
        return JSONResponse(payload)