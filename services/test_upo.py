from analyzer import analyze_company

sample_data = {
    "company_name": "Atlas Robotics Corporation",
    "shareholders": [
        {
            "name": "Pacific Venture Group Ltd",
            "type": "company",
            "sub_entity": {
                "company_name": "Pacific Venture Group Ltd",
                "shareholders": [
                    {
                        "name": "Northern Equity Holdings GmbH",
                        "type": "company",
                        "sub_entity": {
                            "company_name": "Northern Equity Holdings GmbH",
                            "shareholders": [
                                {
                                    "name": "Marcus Schneider",
                                    "type": "individual"
                                }
                            ]
                        }
                    }
                ]
            }
        }
    ]
}

print(analyze_company(sample_data))
