from scripts.ib_inst_utils import init_ib, import_inst_from_ib, app_context
import time

file_name = '../data/refdata/eoddata/HKEX.txt'


app_context = app_context()
broker = init_ib(app_context)

f = open(file_name)
count = 0
for line in f:
    count += 1
    if count == 1:
        continue
    idx = line.find('\t')
    if idx >0:
        symbol = int(line[0:idx])
        desc = line[idx+1:-1]
    else:
        symbol = line
        desc =None

    print "symbol=%s, desc=%s" % (symbol, desc)

    import_inst_from_ib(broker=broker, symbol=str(symbol), exchange='SEHK')

    time.sleep(2)


for inst in app_context.ref_data_mgr.get_all_insts():
    print inst