from sentineltoolbox.models.tasktable import TaskTable

SAMPLE_JSON_TASKTABLE = {
    "version": "06.15",
    "baseline_collection": "OL__L1_.003.03.01",
    "processor_name": "S3A_OL1_RAC",
    "list_of_inputs": [
        {
            "Mode": "ALWAYS",
            "Mandatory": "Yes",
            "Alternatives": [
                {
                    "Order": "1",
                    "Origin": "DB",
                    "Retrieval_Mode": "ValIntersect",
                    "T0": "0",
                    "T1": "0",
                    "File_Type": "S3OLCCR0",
                    "File_Name_Type": "Physical",
                },
                {
                    "Order": "2",
                    "Origin": "DB",
                    "Retrieval_Mode": "ValIntersect",
                    "T0": "0",
                    "T1": "0",
                    "File_Type": "S3OLCCR1",
                    "File_Name_Type": "Physical",
                },
            ],
        },
        {
            "Mode": "ALWAYS",
            "Mandatory": "No",
            "Alternatives": [
                {
                    "Order": "1",
                    "Origin": "DB",
                    "Retrieval_Mode": "ValIntersect",
                    "T0": "5",
                    "T1": "5",
                    "File_Type": "S3NATL0_",
                    "File_Name_Type": "Physical",
                },
            ],
        },
    ],
}
SAMPLE_TASKTABLE = TaskTable(data=SAMPLE_JSON_TASKTABLE)
