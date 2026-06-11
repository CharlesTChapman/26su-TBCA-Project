from collections import Counter
MAJOR_TO_NACE = {'Computer Science': {'isced_f': '06', 'nace': ['J', 'M', 'M_N']}, 'Engineering': {'isced_f': '07', 'nace': ['C', 'F', 'M', 'M_N', 'B-E']}, 'Business Administration': {'isced_f': '04', 'nace': ['K', 'M', 'N', 'M_N', 'G', 'G-I']}, 'Communications': {'isced_f': '03', 'nace': ['J', 'M', 'M_N', 'R', 'R-U', 'R_U']}, 'Sociology': {'isced_f': '03', 'nace': ['O', 'M', 'M_N', 'Q', 'O-Q', 'O_Q']}, 'Psychology': {'isced_f': '09', 'nace': ['Q', 'O-Q', 'O_Q', 'M', 'M_N']}, 'Biology': {'isced_f': '05', 'nace': ['M', 'M_N', 'Q', 'O-Q', 'O_Q']}, 'History': {'isced_f': '02', 'nace': ['P', 'R', 'R-U', 'R_U', 'O', 'O-Q']}, 'English Literature': {'isced_f': '02', 'nace': ['P', 'R', 'J', 'R-U', 'R_U']}}
DEFAULT_NACE = ['M', 'M_N']

def nace_for_major(major):
    entry = MAJOR_TO_NACE.get(major)
    return list(entry['nace']) if entry else list(DEFAULT_NACE)

def resolve_sectors(major, available_sectors):
    available = set(available_sectors)
    hits = [c for c in nace_for_major(major) if c in available]
    if hits:
        return hits
    return [c for c in DEFAULT_NACE if c in available]

def program_weights_from_students(students, available_sectors=None):
    majors = [s['major'] for s in students if s.get('major')]
    counts = Counter(majors)
    if available_sectors is not None:
        counts = Counter({m: n for m, n in counts.items() if resolve_sectors(m, available_sectors)})
    total = sum(counts.values())
    if total == 0:
        return {}
    return {m: n / total for m, n in counts.items()}
if __name__ == '__main__':
    demo_students = [{'major': 'Computer Science'}, {'major': 'Computer Science'}, {'major': 'Engineering'}, {'major': 'Business Administration'}, {'major': 'Psychology'}, {'major': 'History'}, {'major': 'Underwater Basket Weaving'}]
    avail = ['J', 'C', 'K', 'M_N', 'Q', 'P', 'R']
    print('resolve CS:', resolve_sectors('Computer Science', avail))
    print('resolve Psychology:', resolve_sectors('Psychology', avail))
    print('resolve unknown:', resolve_sectors('Underwater Basket Weaving', avail))
    print('weights:', program_weights_from_students(demo_students, avail))
