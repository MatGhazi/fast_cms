

def get_deletion_reasons():
    with open('app/texts/deletion_reasons.txt') as f:
        reasons = [i.strip() for i in f.readlines() if i]
    return reasons


