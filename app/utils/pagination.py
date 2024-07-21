from math import ceil


async def paginate(
    Collection,
    page: int, 
    page_size: int,
    sort: str,
    desc: bool,
    filters: dict = {},
) -> dict:
    """
    Paginates documents in a MongoDB collection using Beanie.

    :param Collection: Beanie Document class representing the MongoDB collection.
    :param page: Integer representing the page number.
    :param page_size: Integer representing the number of documents per page.
    :param sort: String representing the field name to sort by.
    :param desc: Boolean indicating descending (True) or ascending (False) sort.
    :param filters: Dictionary of filter conditions.
    :return: Dictionary containing the count of filtered documents, total pages, and list of items.
    """
    filters = {k:v for k,v in filters.items() if v is not None}
    f_list = []
    for k, v in filters.items():
        if k[2:4] == '__':
            operator, criteria = k.split('__', 1)
        else:
            operator, criteria = 'eq', k
        #
        field = getattr(Collection, criteria)
        match operator:
            case 'eq': f_list.append(field == v)
            case 'ne': f_list.append(field != v)
            case 'gt': f_list.append(field > v)
            case 'ge': f_list.append(field >= v)
            case 'lt': f_list.append(field < v)
            case 'le': f_list.append(field <= v)
            case 'cn': f_list.append({criteria: {'$regex': v, '$options': 'i'}}) 
            # The "i" option makes the search case-insensitive.
    #
    count = await Collection.find(*f_list).count()
    pages = ceil(count / page_size)
    sort_dir = '-' if desc else '+'
    items = await Collection.find(*f_list).sort(sort_dir+sort).skip((page-1)*page_size).limit(page_size).to_list()
    return dict(count=count, pages=pages, items=items)
