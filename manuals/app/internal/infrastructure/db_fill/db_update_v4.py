from datetime import datetime
from typing import List

from app.internal.infrastructure.notion_client import NotionClient
from app.models import PageElement, PageTreeNode

from .content_getters import get_default_element_content, get_image_element_content_webp
from .contents import ROOT_PAGE_ID

notion_client = NotionClient()


def check_db(node: PageTreeNode = None, force_update: bool=False):
    if not node:
        node = PageTreeNode.objects.filter(id=ROOT_PAGE_ID).first()
        if not node:
            raise Exception("No root page node")
    check_page(node.id, node, force_update=force_update)
    for child in node.child_nodes.all():
        check_db(child, force_update=force_update)
    return


def check_page(id: str, node: PageTreeNode, force_update: bool=False):
    page = notion_client.page(id)
    check_page_element(page, 0, node=node, force_update=force_update)


def check_page_element(page_element: dict, order: int, node: PageTreeNode = None, force_update: bool=False):
    print(page_element["id"])
    is_edited, edited_time = edited_check(page_element, node)

    if force_update or is_edited:
        new_element = update_element(page_element, edited_time, order, force_update=force_update)
        if node:
            node.child_page = new_element
            node.save()
        return new_element
    page = PageElement.objects.filter(id=page_element["id"]).first()
    return page


def update_element(page_element: dict, edited_time: datetime, order: int, force_update: bool=False):
    element_id = page_element["id"]
    element_type = page_element["type"]
    if element_type == "image":
        element_content = get_image_element_content_webp(page_element)
    else:
        element_content = get_default_element_content(page_element, element_type)

    if not page_element["has_children"]:

        return save_element(element_id, element_type, element_content, [], edited_time, order)

    children = notion_client.page_children(element_id)
    children_objects = []

    for i in range(len(children["results"])):
        child = children["results"][i]
        children_objects.append(check_page_element(child, i, force_update=force_update))

    return save_element(element_id, element_type, element_content, children_objects, edited_time, order)


def save_element(
    element_id: str,
    element_type: str,
    element_content: dict,
    element_children: List[PageElement],
    edited_time: datetime,
    order: int,
):
    db_item = PageElement(
        id=element_id, type=element_type, content={"content": element_content}, last_edited=edited_time, order=order
    )
    print(element_children)
    element_children = list(filter(lambda x: x, element_children))
    db_item.save()
    element_children_ids = [x.id for x in element_children]
    children_to_add = list(filter(lambda x: not db_item.children.filter(id=x).exists(), element_children_ids))
    children_to_exclude = db_item.children.exclude(id__in=element_children_ids).all()
    db_item.children.remove(*children_to_exclude)
    db_item.children.add(*children_to_add)
    return db_item


def edited_check(item: dict, node: PageTreeNode):
    id = item["id"]
    db_item = PageElement.objects.filter(id=id).first()
    if not db_item:
        if "last_edited_time" not in item.keys():
            return True, datetime.now().astimezone("UTC")
        return True, datetime.fromisoformat(item["last_edited_time"][:-1] + "+00:00")

    last_edited_time = datetime.fromisoformat(item["last_edited_time"][:-1] + "+00:00")
    db_last_edited_time = db_item.last_edited
    if node and (not node.child_page or db_item.id != node.child_page.id):
        node.child_page = db_item
        node.save()
    return (last_edited_time != db_last_edited_time), datetime.fromisoformat(item["last_edited_time"][:-1] + "+00:00")
