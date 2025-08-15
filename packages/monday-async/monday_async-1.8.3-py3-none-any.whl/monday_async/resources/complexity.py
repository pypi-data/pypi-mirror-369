# monday-async
# Copyright 2025 Denys Karmazeniuk
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from monday_async.resources.base_resource import AsyncBaseResource
from monday_async.utils.queries import get_complexity_query


class ComplexityResource(AsyncBaseResource):
    async def get_complexity(self) -> dict:
        """
        Get the current complexity points. For more information visit
        https://developer.monday.com/api-reference/reference/complexity
        """

        query = get_complexity_query()
        return await self.client.execute(query)
