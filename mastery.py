from datetime import datetime,timezone

def update_mastery(current,correct,difficulty=1):
    step=.07+.015*max(0,difficulty-1); value=current+step if correct else current-step*1.20
    return max(0,min(1,value))
def label(value):
    return 'Strong' if value>=.75 else ('Developing' if value>=.50 else 'Needs Practice')
def retention_score(mastery,last_practiced):
    if not last_practiced:return mastery
    try:
        dt=datetime.strptime(last_practiced,'%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        days=max(0,(datetime.now(timezone.utc)-dt).total_seconds()/86400)
        return max(0,mastery-min(.45,days*.035))
    except ValueError:return mastery
def recommendation_score(row):
    r=retention_score(row['mastery'],row['last_practiced'])
    return (1-row['mastery'])*.65+(1-r)*.35
def next_best_concept(concepts):
    return max(concepts,key=recommendation_score) if concepts else None
