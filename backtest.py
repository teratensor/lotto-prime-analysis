#!/usr/bin/env python3
"""
로또 소수 중심 백테스팅 (상세표 스코어링 적용)
- 50회차 학습 → 다음 회차 예측
- 876회차부터 1203회차까지 검증
- 스코어링: 빈도 + 주기 + 최근 + 소수 + 합계 + 콜드 + 위치 + 이월 + 연속
"""

from collections import defaultdict

# 소수 목록
PRIMES = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43}

# 연속수 다빈도 번호 (참여 빈도 기준)
CONSECUTIVE_FREQ = {27: 20, 15: 19, 16: 18, 32: 17, 28: 17, 29: 16, 26: 15, 33: 14, 11: 13, 12: 13}

# 위치별 특화 소수 (position-analysis.md 기준)
PRIME_POSITION_MAP = {
    # ord1 특화: 2, 3이 압도적
    2: [0], 3: [0], 5: [0, 1], 7: [0, 1],
    # ord2 특화: 5, 17, 11, 19
    11: [1, 2], 13: [2, 3],
    # ord3~4 특화: 17, 19, 23, 29
    17: [1, 2, 3], 19: [1, 2, 3], 23: [2, 3, 4], 29: [3, 4],
    # ord5 특화: 37, 29, 31
    31: [3, 4, 5], 37: [4, 5],
    # ord6 특화: 43, 41
    41: [4, 5], 43: [5]
}

# 위치별 선호 끝수 (378회 기준 빈도 분석)
# ord1: 1,2,3,4 / ord2: 5,9,7 / ord3: 1,3,7,9 / ord4: 7,1,8 / ord5: 9,0,3 / ord6: 5,4,2
ENDING_POSITION_PREF = {
    0: {1: 67, 2: 59, 3: 55, 4: 54, 5: 35, 6: 33, 7: 24, 8: 23, 9: 14, 0: 14},  # ord1
    1: {5: 47, 9: 47, 7: 46, 0: 40, 2: 36, 6: 35, 3: 35, 8: 32, 4: 31, 1: 29},  # ord2
    2: {1: 42, 3: 42, 7: 42, 9: 42, 6: 37, 5: 37, 0: 36, 2: 35, 4: 34, 8: 31},  # ord3
    3: {7: 48, 1: 42, 8: 42, 9: 38, 5: 38, 3: 37, 2: 36, 0: 33, 6: 32, 4: 32},  # ord4
    4: {9: 46, 0: 42, 3: 42, 6: 40, 2: 40, 8: 37, 7: 36, 1: 32, 5: 32, 4: 31},  # ord5
    5: {5: 69, 4: 51, 2: 47, 3: 44, 9: 38, 1: 33, 0: 31, 7: 27, 8: 24, 6: 14},  # ord6
}

# 데이터 로드
DATA = """826,14,15,16,19,21,30
827,3,5,16,29,30,31
828,6,7,12,31,40,45
829,9,17,22,28,37,44
830,15,18,22,33,39,43
831,4,11,30,35,37,41
832,6,12,16,23,43,45
833,7,10,11,16,26,39
834,12,17,18,19,20,25
835,7,17,22,31,36,39
836,1,2,5,12,23,40
837,1,7,23,28,31,32
838,7,18,23,29,30,42
839,8,14,22,29,35,42
840,18,19,22,27,30,38
841,9,10,15,18,29,31
842,1,5,13,24,32,39
843,10,11,17,19,29,44
844,3,7,10,16,18,31
845,9,12,22,25,34,40
846,10,21,22,26,38,42
847,2,15,22,26,30,37
848,3,7,8,18,25,27
849,6,10,34,40,41,42
850,2,18,23,25,27,45
851,1,9,25,32,39,44
852,2,6,15,16,28,29
853,4,9,25,28,29,35
854,4,6,10,20,21,26
855,10,14,15,22,28,29
856,6,20,21,38,42,45
857,8,9,24,29,33,42
858,2,12,26,27,30,43
859,2,5,12,19,30,37
860,3,10,11,17,32,33
861,1,15,16,25,36,42
862,7,16,32,33,42,43
863,8,12,31,35,37,43
864,2,19,23,25,30,39
865,3,17,19,21,29,33
866,5,22,26,27,36,42
867,16,25,29,34,40,43
868,3,8,13,17,29,38
869,7,22,24,30,36,41
870,1,15,16,35,38,44
871,1,3,27,30,33,44
872,1,3,12,20,27,34
873,8,11,17,27,29,40
874,7,12,21,29,34,35
875,4,14,25,29,31,42
876,11,33,34,40,42,45
877,7,12,16,17,23,29
878,7,25,34,39,42,45
879,3,9,29,35,44,45
880,13,16,18,30,40,44
881,3,12,15,18,28,38
882,5,8,21,26,38,44
883,18,20,23,36,37,39
884,6,14,18,28,35,43
885,1,2,24,28,32,45
886,6,13,32,33,36,42
887,6,9,16,19,41,44
888,12,15,19,23,24,37
889,13,26,36,41,42,45
890,9,18,20,23,29,39
891,1,9,30,35,39,44
892,4,5,21,34,43,44
893,4,8,10,12,29,32
894,4,5,11,13,26,42
895,5,7,23,33,37,44
896,6,15,20,28,31,35
897,1,9,16,38,43,45
898,6,17,25,27,36,44
899,2,13,19,21,29,38
900,1,9,10,14,33,42
901,3,18,20,32,33,41
902,9,10,20,25,29,37
903,14,31,38,41,44,45
904,7,13,17,19,22,42
905,4,8,18,25,27,33
906,10,19,25,35,40,41
907,5,10,13,33,36,37
908,16,17,19,20,37,41
909,2,5,25,40,41,44
910,5,27,30,32,39,40
911,2,10,12,19,29,33
912,1,13,20,24,32,45
913,4,7,17,26,31,32
914,9,18,24,32,39,40
915,11,14,17,21,22,32
916,16,19,21,30,32,35
917,15,20,29,32,38,41
918,9,17,27,32,33,41
919,7,11,21,23,27,36
920,3,10,17,20,27,29
921,7,10,16,26,33,39
922,8,10,14,17,29,39
923,4,6,7,12,25,32
924,1,12,19,25,37,43
925,3,5,7,11,37,39
926,8,19,20,30,34,38
927,3,4,6,24,27,37
928,2,19,21,36,38,44
929,13,20,33,36,42,43
930,4,9,26,31,34,43
931,14,20,25,27,29,38
932,4,17,23,33,37,38
933,6,9,11,23,25,38
934,6,7,10,14,40,44
935,2,22,23,26,27,36
936,2,13,33,34,36,45
937,6,9,13,27,28,40
938,16,20,24,29,37,45
939,3,17,27,37,39,45
940,1,4,7,11,15,38
941,1,12,29,32,36,38
942,1,11,15,19,21,42
943,14,15,19,27,30,38
944,3,23,29,34,36,39
945,2,12,13,27,30,33
946,3,4,24,28,30,42
947,16,21,24,31,32,41
948,3,9,19,22,31,41
949,4,7,11,13,19,20
950,4,5,30,31,34,41
951,5,8,10,24,34,41
952,2,3,11,20,22,39
953,8,9,13,22,23,45
954,2,8,15,24,38,42
955,7,9,14,16,29,39
956,7,15,22,25,33,35
957,3,8,16,21,32,43
958,1,7,9,21,28,34
959,6,7,18,25,28,38
960,2,10,15,28,37,44
961,5,13,17,29,30,38
962,4,11,15,16,39,40
963,2,6,31,35,37,42
964,15,17,32,37,38,41
965,3,12,17,24,36,40
966,2,7,13,33,39,45
967,9,16,18,28,37,39
968,1,23,24,32,34,37
969,2,17,18,21,29,45
970,4,6,22,27,42,45
971,6,17,25,31,38,42
972,1,6,11,13,16,30
973,5,16,25,28,30,35
974,1,19,31,36,38,40
975,8,15,21,27,38,45
976,9,14,23,24,34,40
977,25,26,27,29,38,40
978,6,9,25,28,30,36
979,5,17,19,30,43,44
980,1,13,16,20,23,35
981,6,12,23,31,35,43
982,1,7,26,27,39,43
983,1,4,13,16,35,37
984,1,14,17,18,36,40
985,16,20,21,26,40,44
986,16,24,31,33,36,37
987,4,5,9,11,23,34
988,18,21,39,42,44,45
989,3,14,15,23,31,38
990,10,19,21,25,30,33
991,8,18,28,31,42,43
992,1,11,12,14,36,40
993,24,25,29,32,33,41
994,1,4,29,38,43,45
995,1,13,20,27,33,44
996,8,28,29,33,38,43
997,4,6,9,22,28,39
998,2,3,20,21,33,36
999,1,5,20,24,25,42
1000,1,17,18,19,33,45
1001,11,14,29,34,42,43
1002,2,13,20,21,23,30
1003,3,7,13,24,36,37
1004,5,20,22,34,39,45
1005,3,5,9,27,36,39
1006,2,11,17,21,42,45
1007,1,6,14,18,36,40
1008,3,24,38,40,44,45
1009,13,28,30,31,38,39
1010,5,17,27,33,35,37
1011,3,5,10,17,26,37
1012,3,4,19,23,31,33
1013,11,15,26,30,34,42
1014,11,19,27,28,41,42
1015,6,12,17,24,26,27
1016,17,20,21,26,28,31
1017,7,14,24,37,40,41
1018,1,3,23,25,31,35
1019,13,27,29,30,36,41
1020,4,12,26,27,33,37
1021,7,14,15,16,21,25
1022,15,21,23,26,29,45
1023,2,11,21,24,25,45
1024,5,17,34,38,40,43
1025,6,19,24,33,36,40
1026,7,10,19,22,28,45
1027,1,6,23,31,37,42
1028,2,5,11,12,35,44
1029,3,10,25,32,35,42
1030,6,10,20,25,30,35
1031,4,10,12,21,26,39
1032,2,6,11,18,31,40
1033,5,7,9,14,26,37
1034,12,27,31,40,41,44
1035,4,6,26,33,36,37
1036,5,12,19,29,38,43
1037,1,2,3,6,36,37
1038,3,11,13,25,36,40
1039,1,4,27,32,33,41
1040,13,15,28,29,41,42
1041,4,9,16,20,39,45
1042,4,6,9,21,31,41
1043,4,11,25,27,31,33
1044,4,10,24,27,39,45
1045,5,6,18,19,42,45
1046,7,26,27,28,36,44
1047,12,17,21,23,26,28
1048,4,27,31,38,40,42
1049,10,18,21,24,26,27
1050,1,17,32,37,39,43
1051,4,9,17,24,40,42
1052,2,6,18,31,34,37
1053,1,3,17,18,24,30
1054,14,15,18,26,28,36
1055,14,15,16,33,35,42
1056,7,10,12,18,23,32
1057,17,18,19,21,23,35
1058,12,18,20,23,33,44
1059,3,5,15,21,30,31
1060,15,19,20,23,33,44
1061,5,11,14,28,36,39
1062,10,28,33,35,40,42
1063,3,15,19,20,25,35
1064,5,7,9,15,31,33
1065,8,13,23,31,32,39
1066,9,15,17,26,30,41
1067,14,23,27,35,36,44
1068,1,10,14,27,31,36
1069,1,2,8,30,32,38
1070,4,5,13,19,24,38
1071,1,4,10,22,34,37
1072,8,12,18,26,32,39
1073,10,20,27,32,42,43
1074,2,3,5,9,19,42
1075,2,9,20,25,40,42
1076,15,16,18,19,24,43
1077,12,16,17,22,29,39
1078,3,5,25,26,28,35
1079,2,4,7,19,25,29
1080,11,22,26,27,29,44
1081,1,13,18,25,27,33
1082,4,15,30,33,35,44
1083,4,10,16,29,34,42
1084,12,20,29,34,40,41
1085,3,7,8,29,34,37
1086,4,10,13,14,23,27
1087,4,5,10,13,28,29
1088,13,22,36,40,41,45
1089,4,5,13,27,32,37
1090,2,6,7,10,32,43
1091,12,13,21,24,27,28
1092,24,25,31,35,37,38
1093,1,12,19,25,30,34
1094,3,6,13,15,16,32
1095,4,6,25,29,34,35
1096,2,10,21,23,42,45
1097,10,21,22,35,37,41
1098,8,18,20,26,35,40
1099,2,23,26,37,40,44
1100,2,9,16,21,22,35
1101,8,11,20,29,33,45
1102,2,17,27,32,35,41
1103,11,19,32,36,40,44
1104,1,2,3,9,18,23
1105,1,26,27,31,32,34
1106,2,3,30,36,38,45
1107,1,7,11,18,39,40
1108,8,9,14,35,40,43
1109,3,22,27,33,39,44
1110,2,9,11,17,20,27
1111,1,3,4,10,29,31
1112,3,6,8,17,25,26
1113,5,21,29,30,38,45
1114,2,12,13,25,39,42
1115,5,13,27,37,41,42
1116,1,10,16,17,33,34
1117,13,18,19,35,37,39
1118,2,9,13,22,25,35
1119,4,19,21,25,28,29
1120,6,8,13,22,30,39
1121,2,6,11,17,36,37
1122,4,5,10,19,44,45
1123,6,10,13,28,32,40
1124,9,19,32,35,37,43
1125,2,14,28,31,36,39
1126,27,28,31,36,39,41
1127,4,6,17,28,31,32
1128,2,8,10,30,36,45
1129,11,12,20,29,38,41
1130,9,11,12,42,43,45
1131,10,14,21,33,35,44
1132,4,10,16,33,43,45
1133,6,9,19,23,24,35
1134,2,7,12,22,37,38
1135,2,3,18,22,34,41
1136,8,20,24,30,35,38
1137,1,11,22,23,25,42
1138,8,14,22,29,35,44
1139,3,4,7,8,17,41
1140,3,17,26,31,39,43
1141,9,22,24,28,37,39
1142,1,9,19,24,27,34
1143,12,13,14,16,23,43
1144,13,15,16,17,23,36
1145,5,14,35,37,38,45
1146,14,20,21,24,37,44
1147,15,20,24,34,35,40
1148,10,11,15,17,22,24
1149,3,13,17,21,39,43
1150,5,7,13,24,26,45
1151,8,11,12,28,34,36
1152,12,18,22,24,35,36
1153,11,19,23,24,30,32
1154,5,10,19,28,29,38
1155,5,16,24,25,36,40
1156,1,2,27,28,29,45
1157,3,6,13,16,35,42
1158,2,21,24,30,32,34
1159,1,3,12,18,25,36
1160,1,2,11,13,27,44
1161,15,19,25,30,31,32
1162,1,19,26,27,33,40
1163,17,24,29,31,38,45
1164,6,11,33,38,40,45
1165,4,9,28,31,34,42
1166,10,14,15,32,37,39
1167,3,5,14,17,25,33
1168,2,14,18,28,31,39
1169,2,19,28,30,35,43
1170,11,27,28,39,44,45
1171,4,11,16,35,42,45
1172,3,9,16,17,33,43
1173,1,16,22,23,31,43
1174,4,26,28,29,32,33
1175,8,9,16,17,23,31
1176,3,12,17,32,39,44
1177,3,8,11,18,39,40
1178,4,8,15,18,37,43
1179,6,13,14,17,28,36
1180,1,5,7,15,23,32
1181,12,17,23,26,27,30
1182,3,13,14,17,20,36
1183,1,11,12,17,18,21
1184,3,4,5,12,22,39
1185,8,13,14,20,29,38
1186,10,15,25,29,35,44
1187,10,15,24,25,31,38
1188,1,3,8,20,21,42
1189,7,19,24,31,32,35
1190,4,7,10,21,23,39
1191,3,5,16,21,22,34
1192,5,10,12,32,34,44
1193,12,15,16,23,24,34
1194,17,18,29,32,33,39
1195,15,22,25,27,41,44
1196,2,5,7,11,19,37
1197,9,21,25,27,34,39
1198,3,9,15,28,32,34
1199,6,8,18,19,28,30
1200,24,32,37,38,40,45
1201,16,18,31,37,40,45
1202,5,16,19,22,23,24
1203,3,8,9,11,12,43"""

def parse_data():
    """데이터 파싱"""
    rows = []
    for line in DATA.strip().split('\n'):
        parts = line.split(',')
        round_num = int(parts[0])
        numbers = [int(x) for x in parts[1:7]]
        rows.append((round_num, numbers))
    return rows

def count_primes(numbers):
    """소수 개수 카운트"""
    return sum(1 for n in numbers if n in PRIMES)

def get_prime_positions(numbers):
    """소수가 출현한 위치들 반환 (0-indexed)"""
    return [i for i, n in enumerate(numbers) if n in PRIMES]

def analyze_training_data(data, start_idx, window=50):
    """학습 데이터 분석"""
    training = data[start_idx:start_idx + window]

    # 위치별 소수 출현 횟수
    pos_prime_count = [0] * 6
    # 위치별 연속 출현 추적 (소수가 같은 위치에서 연속 출현)
    pos_last_prime = [{} for _ in range(6)]  # {소수번호: 마지막출현idx}
    pos_consecutive_primes = [set() for _ in range(6)]  # 연속출현한 소수들

    # 번호별 출현 정보
    num_freq = defaultdict(int)  # 전체 빈도
    num_last = {}  # 마지막 출현 idx
    num_pos_freq = defaultdict(lambda: [0] * 6)  # 번호별 위치별 빈도

    # 연속수 쌍 출현 횟수
    consecutive_pairs = defaultdict(int)

    # 끝수 분석: 위치별 끝수 출현 빈도
    pos_ending_freq = [defaultdict(int) for _ in range(6)]  # [{끝수: 빈도}] * 6

    for idx, (round_num, numbers) in enumerate(training):
        for pos, num in enumerate(numbers):
            num_freq[num] += 1
            num_last[num] = idx
            num_pos_freq[num][pos] += 1

            # 끝수 빈도 기록
            ending = num % 10
            pos_ending_freq[pos][ending] += 1

            if num in PRIMES:
                pos_prime_count[pos] += 1
                # 같은 위치에서 같은 소수가 연속 출현 체크
                if num in pos_last_prime[pos] and pos_last_prime[pos][num] == idx - 1:
                    pos_consecutive_primes[pos].add(num)
                pos_last_prime[pos][num] = idx

        # 연속수 쌍 카운트
        for i in range(5):
            if numbers[i + 1] - numbers[i] == 1:
                consecutive_pairs[(numbers[i], numbers[i + 1])] += 1

    # 소수 개수 분포
    prime_count_dist = defaultdict(int)
    for _, numbers in training:
        cnt = count_primes(numbers)
        prime_count_dist[cnt] += 1

    return {
        'pos_prime_count': pos_prime_count,
        'pos_consecutive_primes': pos_consecutive_primes,
        'num_freq': num_freq,
        'num_last': num_last,
        'num_pos_freq': num_pos_freq,
        'prime_count_dist': prime_count_dist,
        'consecutive_pairs': consecutive_pairs,
        'pos_ending_freq': pos_ending_freq,
        'window': window,
        'training': training
    }

def score_number(num, analysis, last_round_numbers, detail=False):
    """번호별 스코어 계산 (상세표 완전 적용)

    Args:
        num: 번호 (1-45)
        analysis: 분석 데이터
        last_round_numbers: 직전 회차 번호
        detail: True면 각 요소별 점수 딕셔너리 반환

    Returns:
        detail=False: 총점 (float)
        detail=True: {요소별 점수 딕셔너리}
    """
    window = analysis['window']
    scores = {}

    # 연속출현 제외 체크 (소수가 같은 위치에서 연속 출현 시 완전 제외)
    excluded = False
    if num in PRIMES:
        for pos in range(6):
            if num in analysis['pos_consecutive_primes'][pos]:
                excluded = True
                break

    if excluded:
        if detail:
            return {'excluded': True, 'total': float('-inf')}
        return float('-inf')

    # 1. 빈도 점수 (최대 ~6)
    freq = analysis['num_freq'].get(num, 0)
    freq_score = min(freq / 8, 6)
    scores['빈도'] = round(freq_score, 1)

    # 2. 주기 점수 (최대 10)
    last = analysis['num_last'].get(num, -50)
    gap = window - last - 1
    cycle_score = min(gap / 5, 10)
    scores['주기'] = round(cycle_score, 1)

    # 3. 최근 감점 (최대 -4)
    recent_penalty = 0
    if gap <= 2:
        recent_penalty = -((3 - gap) * 2)
    scores['최근'] = round(recent_penalty, 1)

    # 4. 소수 점수 (3점)
    prime_score = 3 if num in PRIMES else 0
    scores['소수'] = round(prime_score, 1)

    # 5. 소수위치 점수 (최대 2점)
    prime_pos_score = 0
    if num in PRIME_POSITION_MAP:
        preferred_positions = PRIME_POSITION_MAP[num]
        pos_freq = analysis['num_pos_freq'].get(num, [0] * 6)
        specialized_freq = sum(pos_freq[p] for p in preferred_positions if p < len(pos_freq))
        if specialized_freq > 0:
            prime_pos_score = min(specialized_freq / 3, 2)
    scores['소수위치'] = round(prime_pos_score, 1)

    # 6. 콜드 점수 (3점)
    avg_cycle = 7
    cold_score = 3 if gap > avg_cycle else 0
    scores['콜드'] = round(cold_score, 1)

    # 7. 위치빈도 점수 (최대 ~3)
    pos_freq = analysis['num_pos_freq'].get(num, [0] * 6)
    max_pos_freq = max(pos_freq) if pos_freq else 0
    position_score = min(max_pos_freq / 5, 3)
    scores['위치'] = round(position_score, 1)

    # 8. 이월 점수 (2점)
    carryover_score = 2 if num in last_round_numbers else 0
    scores['이월'] = round(carryover_score, 1)

    # 9. 연속수 점수 (최대 ~2)
    consecutive_score = 0
    if num in CONSECUTIVE_FREQ:
        consecutive_score = min(CONSECUTIVE_FREQ[num] / 10, 2)
    for (a, b), cnt in analysis['consecutive_pairs'].items():
        if num == a or num == b:
            consecutive_score = max(consecutive_score, min(cnt / 3, 2))
    scores['연속'] = round(consecutive_score, 1)

    # 10. 끝수 점수 (최대 ~0.5)
    ending = num % 10
    ending_score = 0
    pos_ending_freq = analysis.get('pos_ending_freq', [])
    for pos in range(6):
        if pos < len(pos_ending_freq):
            learned_freq = pos_ending_freq[pos].get(ending, 0)
            global_pref = ENDING_POSITION_PREF.get(pos, {}).get(ending, 30)
            combined = learned_freq * 0.7 + (global_pref / 10) * 0.3
            ending_score = max(ending_score, min(combined / 5, 0.5))
    scores['끝수'] = round(ending_score, 2)

    # 총점 계산
    total = sum(scores.values())
    scores['총점'] = round(total, 1)
    scores['excluded'] = False

    if detail:
        return scores
    return total

def get_full_score_table(analysis, last_round_numbers):
    """45개 번호 전체 상세 점수표 생성"""
    all_scores = []
    for num in range(1, 46):
        detail = score_number(num, analysis, last_round_numbers, detail=True)
        detail['번호'] = num
        detail['P'] = 'P' if num in PRIMES else ''
        all_scores.append(detail)

    # 총점 기준 내림차순 정렬
    all_scores.sort(key=lambda x: x.get('총점', float('-inf')), reverse=True)

    # 순위 부여
    for i, s in enumerate(all_scores):
        s['순위'] = i + 1

    return all_scores


def predict_top_numbers(analysis, last_round_numbers, top_n=10):
    """TOP N 번호 예측 (합계범위 101-160 고려)"""
    scores = []
    for num in range(1, 46):
        total_score = score_number(num, analysis, last_round_numbers)
        scores.append((num, total_score))

    # 연속출현 제외된 번호(-inf) 필터링
    valid_scores = [(n, s) for n, s in scores if s > float('-inf')]
    valid_scores.sort(key=lambda x: -x[1])

    # TOP 후보군에서 합계범위 101-160 적합도 가산
    top_candidates = valid_scores[:20]

    # 각 번호별 합계 적합도 계산 (평균값 136 기준으로 기여도)
    enhanced_scores = []
    for num, base_score in top_candidates:
        sum_bonus = 0
        # 합계 136을 만들기 위한 개별 번호 평균값은 약 22.7
        # 17-27 범위 번호는 합계 범위에 유리
        if 17 <= num <= 27:
            sum_bonus = 1.0
        elif 12 <= num <= 32:
            sum_bonus = 0.5
        enhanced_scores.append((num, base_score + sum_bonus))

    enhanced_scores.sort(key=lambda x: -x[1])
    return enhanced_scores[:top_n]

def run_backtest():
    """백테스팅 실행"""
    data = parse_data()
    data_dict = {r: nums for r, nums in data}

    results = []
    last_full_table = None  # 마지막 회차의 전체 상세표

    # 876회차부터 1203회차까지 예측
    for target_round in range(876, 1204):
        # 학습 범위: target_round - 50 ~ target_round - 1
        start_round = target_round - 50

        # 데이터 인덱스 찾기
        start_idx = None
        for i, (r, _) in enumerate(data):
            if r == start_round:
                start_idx = i
                break

        if start_idx is None:
            continue

        # 분석
        analysis = analyze_training_data(data, start_idx, 50)

        # 직전 회차 번호
        last_round = target_round - 1
        last_numbers = data_dict.get(last_round, [])

        # TOP 10 예측
        top10 = predict_top_numbers(analysis, last_numbers, 10)
        top10_nums = set(n for n, _ in top10)

        # 실제 당첨번호
        actual = data_dict.get(target_round, [])
        if not actual:
            continue

        # 적중 개수
        hits = len(set(actual) & top10_nums)

        # 소수 분석
        actual_primes = [n for n in actual if n in PRIMES]
        predicted_primes = [n for n, _ in top10 if n in PRIMES]
        prime_hits = len(set(actual_primes) & set(predicted_primes))

        # 마지막 회차면 전체 상세표 저장
        if target_round == 1203:
            last_full_table = {
                'round': target_round,
                'actual': actual,
                'last_numbers': last_numbers,
                'table': get_full_score_table(analysis, last_numbers)
            }

        results.append({
            'round': target_round,
            'actual': actual,
            'top10': [n for n, _ in top10],
            'hits': hits,
            'actual_primes': actual_primes,
            'predicted_primes': predicted_primes,
            'prime_hits': prime_hits
        })

    return results, last_full_table

def generate_report(results, full_table=None):
    """결과 리포트 생성"""
    total = len(results)

    # 적중률 통계
    hit_dist = defaultdict(int)
    prime_hit_dist = defaultdict(int)
    total_hits = 0
    total_prime_hits = 0

    for r in results:
        hit_dist[r['hits']] += 1
        prime_hit_dist[r['prime_hits']] += 1
        total_hits += r['hits']
        total_prime_hits += r['prime_hits']

    avg_hits = total_hits / total if total > 0 else 0
    avg_prime_hits = total_prime_hits / total if total > 0 else 0

    report = f"""# 백테스팅 결과 보고서

## 개요

- **테스트 기간**: 876회차 ~ 1203회차 ({total}회)
- **학습 방식**: 50회차 학습 → 다음 회차 예측
- **예측 방식**: TOP 10 번호 선정

## 적중률 통계

### 전체 적중 분포 (TOP 10 중)

| 적중 개수 | 횟수 | 비율 |
|:--:|:--:|:--:|
"""

    for i in range(7):
        cnt = hit_dist.get(i, 0)
        pct = cnt / total * 100 if total > 0 else 0
        report += f"| {i}개 | {cnt} | {pct:.1f}% |\n"

    report += f"""
**평균 적중**: {avg_hits:.2f}개/회

### 소수 적중 분포

| 적중 개수 | 횟수 | 비율 |
|:--:|:--:|:--:|
"""

    for i in range(5):
        cnt = prime_hit_dist.get(i, 0)
        pct = cnt / total * 100 if total > 0 else 0
        report += f"| {i}개 | {cnt} | {pct:.1f}% |\n"

    report += f"""
**평균 소수 적중**: {avg_prime_hits:.2f}개/회

## 상세 결과 (최근 30회)

| 회차 | 당첨번호 | TOP10 예측 | 적중 | 소수적중 |
|:--:|:--|:--|:--:|:--:|
"""

    for r in results[-30:]:
        actual_str = ','.join(map(str, r['actual']))
        top10_str = ','.join(map(str, r['top10']))
        # 적중 번호 표시
        hits_nums = set(r['actual']) & set(r['top10'])
        hits_str = ','.join(map(str, sorted(hits_nums))) if hits_nums else '-'
        report += f"| {r['round']} | {actual_str} | {top10_str} | {r['hits']}({hits_str}) | {r['prime_hits']} |\n"

    report += f"""
## 전체 상세 결과

<details>
<summary>전체 {total}회 결과 보기</summary>

| 회차 | 당첨번호 | TOP10 예측 | 적중 | 소수적중 |
|:--:|:--|:--|:--:|:--:|
"""

    for r in results:
        actual_str = ','.join(map(str, r['actual']))
        top10_str = ','.join(map(str, r['top10']))
        hits_nums = set(r['actual']) & set(r['top10'])
        hits_str = ','.join(map(str, sorted(hits_nums))) if hits_nums else '-'
        report += f"| {r['round']} | {actual_str} | {top10_str} | {r['hits']}({hits_str}) | {r['prime_hits']} |\n"

    report += """
</details>

"""

    # 전체 상세표 추가
    if full_table:
        t = full_table
        actual_set = set(t['actual'])

        # 제외된 번호 목록
        excluded_nums = [s['번호'] for s in t['table'] if s.get('excluded')]

        report += f"""## {t['round']}회차 전체 상세 점수표

- **실제 당첨번호**: {', '.join(map(str, t['actual']))}
- **이월 대상 (직전회차)**: {', '.join(map(str, t['last_numbers']))}
- **연속출현 제외**: {', '.join(map(str, sorted(excluded_nums))) if excluded_nums else '없음'}

| 순위 | 번호 | 빈도 | 주기 | 최근 | 소수 | 소수위치 | 콜드 | 위치 | 이월 | 연속 | 끝수 | 총점 | 당첨 |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
"""
        for s in t['table']:
            num = s['번호']
            p_mark = s['P']
            hit_mark = '★' if num in actual_set else ''

            if s.get('excluded'):
                # 제외된 번호는 별도 표시
                report += f"| - | {num}{p_mark} | - | - | - | - | - | - | - | - | - | - | 제외 | {hit_mark} |\n"
            else:
                report += f"| {s['순위']} | {num}{p_mark} | {s['빈도']} | {s['주기']} | {s['최근']} | {s['소수']} | {s['소수위치']} | {s['콜드']} | {s['위치']} | {s['이월']} | {s['연속']} | {s['끝수']} | {s['총점']} | {hit_mark} |\n"

        # 당첨번호 분포 요약
        hit_ranks = []
        excluded_hits = []
        for s in t['table']:
            if s['번호'] in actual_set:
                if s.get('excluded'):
                    excluded_hits.append(s['번호'])
                else:
                    hit_ranks.append(s['순위'])
        hit_ranks.sort()
        report += f"\n**당첨번호 순위 분포**: {', '.join(map(str, hit_ranks))}"
        if excluded_hits:
            report += f" (제외된 당첨번호: {', '.join(map(str, sorted(excluded_hits)))})"
        report += "\n"

    report += """
## 결론

이 백테스팅은 50회차 데이터를 학습하여 다음 회차 TOP 10 번호를 예측한 결과입니다.
스코어링 요소: 빈도, 주기, 최근감점, 소수, 소수위치, 콜드, 위치빈도, 이월, 연속, 끝수
"""

    return report

if __name__ == '__main__':
    print("백테스팅 시작...")
    results, full_table = run_backtest()
    print(f"총 {len(results)}회차 테스트 완료")

    report = generate_report(results, full_table)

    with open('docs/backtesting.md', 'w', encoding='utf-8') as f:
        f.write(report)

    print("결과 저장: docs/backtesting.md")

    # 요약 출력
    total_hits = sum(r['hits'] for r in results)
    avg = total_hits / len(results) if results else 0
    print(f"평균 적중: {avg:.2f}개/회")
