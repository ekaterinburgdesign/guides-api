from datetime import datetime

from app.internal.infrastructure.notion_client import NotionClient
from app.models import PageElement, PageTreeNode

from .content_getters import get_default_element_content, get_image_element_content_webp

notion_client = NotionClient()


def check_db():
    pages = PageTreeNode.objects.all()
    for page in pages:
        check_page(page.id, page)
    return


def check_page(id, node):
    page = notion_client.page(id)
    check_page_element(page, node)


def check_page_element(page_element, node=None):
    print(page_element["id"])
    is_edited, edited_time = edited_check(page_element, node)

    if is_edited:
        new_element = update_element(page_element, edited_time)
        if node:
            node.child_page = new_element
            node.save()
        return new_element


def update_element(page_element, edited_time):
    element_id = page_element["id"]
    element_type = page_element["type"]
    if element_type == "image":
        element_content = get_image_element_content_webp(page_element)
    else:
        element_content = get_default_element_content(page_element, element_type)

    if not page_element["has_children"]:

        return save_element(element_id, element_type, element_content, [], edited_time)

    children = notion_client.page_children(element_id)
    children_objects = []

    for child in children["results"]:
        children_objects.append(check_page_element(child))

    return save_element(element_id, element_type, element_content, children_objects, edited_time)


def save_element(element_id, element_type, element_content, element_children, edited_time):
    db_item = PageElement(
        id=element_id,
        type=element_type,
        content={"content": element_content},
        last_edited=edited_time,
    )
    db_item.save()
    db_item.children.add(*element_children)
    return db_item


def edited_check(item, node):
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
