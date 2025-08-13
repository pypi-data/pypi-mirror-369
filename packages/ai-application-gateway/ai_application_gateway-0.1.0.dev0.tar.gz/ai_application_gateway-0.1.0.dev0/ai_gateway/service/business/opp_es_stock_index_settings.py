# 股票信息索引配置
stock_index_settings = {
    "settings": {
        "analysis": {
            "filter": { 
                "pinyin_full": { 
                    "type": "pinyin",
                    "keep_first_letter": True,       # 开启首字母缩写（如：芯海→xh）
                    "keep_separate_first_letter": False,  # 不拆分首字母
                    "keep_full_pinyin": True,        # 保留完整拼音分词（zhong guo）
                    "keep_joined_full_pinyin": True, # 保留连写全拼（zhongguo）
                    "keep_none_chinese": True,       # 保留非中文字符（如股票代码中的.SH）
                    "lowercase": True               # 统一转小写
                },
                "stopwords_filter": {  # 停用词
                    "type": "stop",
                    "stopwords": ["公司", "集团", "股份", "有限"]
                }
            },
            "analyzer": {
                "pinyin_analyzer": {
                    "tokenizer": "pinyin",
                    "filter": [
                        "lowercase",
                        "pinyin_full"
                    ]
                },
                "ik_smart": {
                    "type": "custom",
                    "tokenizer": "ik_smart",
                    "filter": [
                        "stopwords_filter",  # 确保停用词过滤器在过滤链中
                        "lowercase"          # 新增：统一转小写
                    ]
                },
                "ik_max_word": {
                    "type": "custom",
                    "tokenizer": "ik_max_word",
                    "filter": [
                        "stopwords_filter",  # 确保停用词过滤器在过滤链中
                        "lowercase"          # 新增：统一转小写
                    ]
                }
            }
        },
        "number_of_shards": 1,  # 索引有1个主分片，生产环境建议根据集群规模调整
        "number_of_replicas": 1 # 每个主分片有1个副本
    },
    "mappings": {
        "dynamic": "strict",  # 禁止动态添加字段
        "properties": {
            # 股票主键 ID
            "id" : {
              "type" : "integer"
            },
            "stock_code": { # 股票代码，如：688595.SH
                "type": "text", # 支持模糊查询
                "fields": {
                    "keyword": {"type": "keyword"}  # 保留关键字字段
                }
            },
            "comp_name": {  # 公司简称，如：芯海科技
                "type": "text", # 支持模糊查询
                "analyzer": "ik_max_word",  # 索引时细粒度分词
                "search_analyzer": "ik_smart",  # 新增：搜索时粗粒度分词
                "fields": {
                    "keyword": {"type": "keyword"},
                    "pinyin": {
                        "type": "text",
                        "analyzer": "pinyin_analyzer"
                    }
                }
            },
            "comp_full_name": { # 公司全称，如：芯海科技（深圳）股份有限公司
                "type": "text", # 支持模糊查询
                "analyzer": "ik_max_word",  # 索引时细粒度分词
                "search_analyzer": "ik_smart",  # 新增：搜索时粗粒度分词
                "fields": {
                    "keyword": {"type": "keyword"},
                    "pinyin": {
                        "type": "text",
                        "analyzer": "pinyin_analyzer"
                    }
                }
            },
            "comp_name_code": { #  公司名称代码，如：芯海科技 (688595.SH)
                "type": "text",  # 支持模糊查询
                "analyzer": "ik_max_word",  # 索引时细粒度分词
                "search_analyzer": "ik_smart",  # 新增：搜索时粗粒度分词
                "fields": {
                    "keyword": {"type": "keyword"},
                    "pinyin": {
                        "type": "text",
                        "analyzer": "pinyin_analyzer"
                    }
                }
            },
            # 股票市场：A股、港股、美股
            "stock_market" : {
              "type" : "keyword"
            },
            # 股票是否有公告：0-否、1-是
            "exist_anns" : {
              "type" : "integer"
            }
        }
    }
}

# 股票信息索引配置
# 该配置用于支持股票名称、股票代码、简拼、全拼的模糊查询
# 支持拼音首字母缩写（如：芯海→xh）
# 支持中文中缀模糊匹配（如：芯海科技→xhkj）
# 支持英文中缀模糊匹配（如：XHKJ→xhkj）
# 支持拼音全拼匹配（如：xinhaikeji→xinhaikeji）
# 支持拼音连写全拼匹配（如：xinhaikeji→xinhaikeji）
# 支持非中文字符匹配（如：股票代码中的.SH）
# 支持统一转小写
# 支持停用词过滤
# 支持N-gram支持中文中缀模糊匹配
stock_index_settings2 = {
    "settings": {
        "analysis": {
            "filter": { 
                "pinyin_full": { 
                    "type": "pinyin",
                    "keep_first_letter": True,       # 开启首字母缩写（如：芯海→xh）
                    "keep_separate_first_letter": False,  # 不拆分首字母
                    "keep_full_pinyin": True,        # 保留完整拼音分词（zhong guo）
                    "keep_joined_full_pinyin": True, # 保留连写全拼（zhongguo）
                    "keep_none_chinese": True,       # 保留非中文字符（如股票代码中的.SH）
                    "lowercase": True               # 统一转小写
                },
                "stopwords_filter": {  # 停用词
                    "type": "stop",
                    "stopwords": ["公司", "集团", "股份", "有限"]
                }
            },
            "analyzer": {
                "pinyin_analyzer": {
                    "tokenizer": "pinyin",
                    "filter": [
                        "lowercase",
                        "pinyin_full"
                    ]
                },
                "ngram_analyzer": {
                    "tokenizer": "ngram_tokenizer"
                },
                "edge_ngram_analyzer": {
                      "tokenizer": "edge_ngram_tokenizer"
                 }
            },
            "tokenizer": {
                "ngram_tokenizer": {
                    "type": "ngram",
                    "min_gram": 2,
                    "max_gram": 3
                },
                "edge_ngram_tokenizer": {
                    "type": "edge_ngram", # 自动生成数字前缀片段，可显著提升 Completion Suggester 对数字的支持能力。
                    "min_gram": 1,
                    "max_gram": 6
                 }
            }
        },
        "number_of_shards": 1,  # 索引有1个主分片，生产环境建议根据集群规模调整
        "number_of_replicas": 1 # 每个主分片有1个副本
    },
    "mappings": {
        "dynamic": "strict",  # 禁止动态添加字
        "properties": {
            # 股票主键 ID
            "id" : {
              "type" : "integer"
            },
            "stock_suggest": {  # 前缀补全,使用Completion Suggester实现毫秒级前缀匹配
                "type": "completion",
                "analyzer": "edge_ngram_analyzer",    # 关键点，用了edge_ngram才能对股票代码（数字）进行拆分，前缀匹配，示例数据：{ "input": ["601106.SH", "中国平安", "zgpn", "zhonggoupingan"], "weight": 10 }， 默认用的是 simple_ngram，只能对中文进行拆分，前缀匹配
                "preserve_separators": True,
                "contexts": [   # 使用上下文过滤（Context Suggester）​
                    {
                        "name": "exist_anns_filter",
                        "type": "category",
                        "path": "exist_anns"
                    }
                ]
            },
            # 股票代码字段
            "stock_code": { # 股票代码，如：688595.SH
                "type": "text", # 支持模糊查询
                "fields": {
                    "keyword": {"type": "keyword"}  # 保留关键字字段
                }
            },
            # 股票简称 - 使用N-gram支持中/英文中缀模糊匹配
            "comp_name": {
                "type": "text",
                "analyzer": "ngram_analyzer",
                "fields": {
                    "pinyin": {
                        "type": "text",
                        "analyzer": "pinyin_analyzer"
                    }
                }
            },
            # 股票全称
            "comp_full_name": {
                "type": "text",
                "analyzer": "ngram_analyzer",
                "fields": {
                    "pinyin": {
                        "type": "text",
                        "analyzer": "pinyin_analyzer"
                    }
                }
            },
            # 股票简称和股票代码
            "comp_name_code": {
                "type": "text",
                "analyzer": "ngram_analyzer",
                "fields": {
                    "pinyin": {
                        "type": "text",
                        "analyzer": "pinyin_analyzer"
                    }
                }
            },
            # 股票市场：A股、港股、美股
            "stock_market" : {
              "type" : "keyword"
            },
            # 股票是否有公告：0-否、1-是
            "exist_anns" : {
              "type" : "keyword"
            }
        }
    }
}
