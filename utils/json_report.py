import json

def generate_json_report(input_filename,results,output_path,threshold=30):
    report_data={
        "input_file":input_filename,
        "threshold": threshold,
        "matches":results
    }
    with open(output_path,"w",encoding="utf-8") as f:
        json.dump(report_data,f,indent=2,ensure_ascii=False)