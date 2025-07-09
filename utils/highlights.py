from difflib import SequenceMatcher

def get_matching_blocks(a:str,b:str,min_len:int=20):
    matcher=SequenceMatcher(None,a,b)
    matches=matcher.get_matching_blocks()
    results=[]
    seen=set()
    for match in matches:
        if match.size>=min_len:
            segment=a[match.a:match.a+match.size]
            if segment in seen:
                continue
            seen.add(segment)
            results.append({
                'text':segment,
                'start_pos':match.a,
                'end_pos':match.a+match.size
            })
    return results
