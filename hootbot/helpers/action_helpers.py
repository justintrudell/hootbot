def trim_payload(full_str, payload):
    """
    Trims the header payload from the full payload string.
    :param full_str: The full payload string provided by the POST request.
    :param payload: The payload to be trimmed, as a Payloads enum object
    :return: Trimmed payload
    """
    return full_str.replace(("%s?=" % payload.value), "", 1)


def optimize_link_list(link_list):
    """
    Optimizes the list of links such that each grouping has no more than 4 elements and
    the video and blog posts are grouped together as much as possible. (TODO)
    :param link_list: List of ArticleLink objects to be optimized.
    :return: The optimized list of ArticleLink objects.
    """
    if not link_list or len(link_list) < 2:
        raise ValueError("Invalid link list of size %d provided - cannot create link list." % len(link_list))
    elif len(link_list) > 8:
        raise ValueError("Link list exceeded 8 elements - cannot create link list.")

    # If the list has 4 or less elements, this can all fit in one list so simply return it,
    # sorted by blog and video.
    if len(link_list) <= 4:
        return [link_list]

    return [link_list[:4], link_list[4:]]