"""
Does waiting for a quieter hour help, if you are going to the ER today?

Quebec's live page tells you how full an ER is right now. This asks a different
question: if you are deciding today, is it worth waiting for the hour that this
facility is historically quieter, within the next six hours?

For every (facility, day, hour) in the archive, the script picks the hour in the
following six with the lowest historical median queue -- computed leaving that
day's own readings out, so the choice never sees the answer -- and compares the
queue actually observed at that hour against the queue at the moment of the
decision.

Run from the repo root:  python3 scripts/same-day-hour-choice.py
Writes data/same-day-hour-choice.csv.
"""
import csv, statistics as st, collections
rows=[]
with open('data/er-hourly.csv', newline='') as f:
    for r in csv.DictReader(f):
        w=(r.get('waiting') or '').strip().strip('\r')
        if not w: continue
        ts=r['ts_local'].strip()
        try: w=int(float(w))
        except: continue
        rows.append((r['slug'].strip(), r['facility_name'].strip(), r['region_name'].strip(), ts[:10], int(ts[11:13]), w))
byfac=collections.defaultdict(lambda: collections.defaultdict(dict)); names={}
for slug,name,region,day,hour,w in rows:
    byfac[slug][day][hour]=w; names[slug]=(name,region)
WIN=6; out=[]; T=collections.Counter(); allgain=[]
for slug, days in byfac.items():
    daylist=sorted(days)
    if len(daylist)<5: continue
    hs=collections.defaultdict(list)
    for d in daylist:
        for h,w in days[d].items(): hs[h].append((d,w))
    win_=tie=loss=0; gains=[]
    for d in daylist:
        hrs=days[d]
        for h in sorted(hrs):
            cand=[x for x in range(h+1,h+1+WIN) if x<24 and x in hrs]
            best=None;bestmed=None
            for c in cand:
                vals=[w for (dd,w) in hs[c] if dd!=d]
                if len(vals)<3: continue
                m=st.median(vals)
                if bestmed is None or m<bestmed: bestmed,best=m,c
            if best is None: continue
            delta=hrs[h]-hrs[best]
            if delta>0: win_+=1; gains.append(delta)
            elif delta==0: tie+=1
            else: loss+=1; gains.append(delta)
    n=win_+tie+loss
    if n<50: continue
    dec=win_+loss
    out.append({'facility':names[slug][0],'region':names[slug][1],'slug':slug,'decisions':n,
      'no_difference_pct':round(100*tie/n,1),
      'better_pct_when_it_mattered':round(100*win_/dec,1) if dec else '',
      'median_people_fewer':st.median(gains) if gains else 0,
      'mean_people_fewer':round(st.mean(gains),2) if gains else 0})
    T['win']+=win_;T['tie']+=tie;T['loss']+=loss; allgain+=gains
n=T['win']+T['tie']+T['loss']; dec=T['win']+T['loss']
print('PROVINCE decisions=%d  no_difference=%.1f%%  better_when_it_mattered=%.1f%%  median_fewer=%s mean_fewer=%.2f'%(
 n,100*T['tie']/n,100*T['win']/dec,st.median(allgain),st.mean(allgain)))
out.sort(key=lambda o:(-(o['better_pct_when_it_mattered'] or 0), o['no_difference_pct']))
mat=[o for o in out if o['no_difference_pct']<50]
print('facilities scored=%d ; where the hour choice matters in >50%% of hours=%d'%(len(out),len(mat)))
print('of those %d, the quieter hour is the better bet in >50%% of cases: %d'%(len(mat),sum(1 for o in mat if o['better_pct_when_it_mattered']>50)))
print()
for o in out[:6]: print(' %-44s %-16s n=%-4d nodiff=%4.1f%%  better=%5.1f%%  med=%+g'%(o['facility'][:44],o['region'][:16],o['decisions'],o['no_difference_pct'],o['better_pct_when_it_mattered'],o['median_people_fewer']))
import csv as c2
with open('data/same-day-hour-choice.csv','w',newline='') as f:
    w=c2.DictWriter(f,fieldnames=['facility','region','slug','decisions','no_difference_pct','better_pct_when_it_mattered','median_people_fewer','mean_people_fewer'])
    w.writeheader(); [w.writerow(o) for o in out]
print('\nwrote', len(out),'rows')
