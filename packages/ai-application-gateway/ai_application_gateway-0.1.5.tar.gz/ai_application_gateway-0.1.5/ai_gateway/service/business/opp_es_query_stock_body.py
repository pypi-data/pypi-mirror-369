# 获取查询股票的body
def get_query_stock_body(keyword, size, exist_anns=None):
    query_body = {
        "query": {
            "bool": {
                "should": [
                    # 模糊查询条件
                    {
                        "wildcard": {
                            "stock_code": f"*{keyword}*"
                        }
                    },
                    # 中文模糊查询条件
                    {
                        "match": {
                            "comp_name": {
                                "query": keyword,
                                "operator": "and"   # 多个词汇时（如"中信 证券"），必须同时包含所有词汇的股票才会被匹配
                            }
                        }
                    },
                    # {
                    #     "match": {
                    #         "comp_full_name": {
                    #             "query": keyword,
                    #             "operator": "and"   # 多个词汇时（如"中信 证券"），必须同时包含所有词汇的股票才会被匹配
                    #         }
                    #     }
                    # }
                    # ,
                    # 拼音查询
                    {
                        "match": {
                            "comp_name.pinyin": keyword
                        }
                    }
                    # ,
                    # {
                    #     "match": {
                    #         "comp_full_name.pinyin": keyword
                    #     }
                    # }
                ],
                "minimum_should_match": 1
            }
        },
        "highlight": {
            "fields": {
                "comp_name": {},
                "stock_code": {}
            }
        },
        "size": size
    }
    
    if exist_anns is not None:
        query_body["query"]["bool"]["filter"] = {
            "term": {
                "exist_anns": exist_anns
            }
        }
    
    return query_body


def get_query_stock_body2(keyword, size, exist_anns=None):
    query_body = {
        "suggest": {
            "stock_suggest": {
                "prefix": keyword,
                "completion": {
                    "field": "stock_suggest",
                    "skip_duplicates": True,
                    "size": size,
                    "fuzzy": {
                        "fuzziness": 0, # 完全匹配允许的编辑距离（0-2）0：完全匹配（默认值）、1：允许1个字符的差异、2：允许2个字符的差异
                        "prefix_length": 0  # 必须匹配的前缀长度 0：从第一个字符开始就可以模糊匹配、大于0：前N个字符必须精确匹配
                    }
                }
            }
        }
    }

    # 过滤公告状态
    if exist_anns is not None:
        # 使用上下文过滤（Context Suggester）​
        # 注意：这里的上下文过滤是针对Completion Suggester的结果进行的，而不是直接针对字段进行过滤。
        # 因此，需要在Completion Suggester的结果中添加一个额外的字段来存储上下文信息。
        # 在索引时，可以将股票的状态（如是否有公告）作为一个额外的字段存储在Completion Suggester的结果中。
        # 然后，在查询时，可以使用这个额外的字段来过滤Completion Suggester的结果。
        query_body["suggest"]["stock_suggest"]["completion"]["contexts"] = {
            "exist_anns_filter": [exist_anns]
        }
    else:
        query_body["suggest"]["stock_suggest"]["completion"]["contexts"] = {
            "exist_anns_filter": [0, 1]  # 默认查询所有状态
        }

    return query_body
