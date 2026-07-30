#include <algorithm>
#include <array>
#include <bitset>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

#include "transcript_sha256.hpp"

#ifndef SIDE
#define SIDE 29
#endif
namespace triangle_mitm {
constexpr int V=SIDE;
static_assert(2*V<=64,"this verifier uses one 64-bit visited-set mask");
using Line=std::array<int,3>;
struct Counts {std::uint64_t states=0,attempted=0,pair=0,c8=0,c16=0,completions=0;Counts&operator+=(const Counts&o){states+=o.states;attempted+=o.attempted;pair+=o.pair;c8+=o.c8;c16+=o.c16;completions+=o.completions;return *this;}};
struct HalfPath { unsigned char endpoint; std::uint64_t mask; };
struct Branch {
 std::vector<Line> lines; std::array<std::vector<int>,V> through; std::array<int,V> degree{}; std::array<std::bitset<V>,V> together{}; int introduced=6; Counts count; transcript_audit::SearchTranscript transcript;
 void insert(Line e){int id=lines.size();lines.push_back(e);for(int p:e){degree[p]++;through[p].push_back(id);}for(int i=0;i<3;i++)for(int j=i+1;j<3;j++){together[e[i]].set(e[j]);together[e[j]].set(e[i]);}}
 void erase(){Line e=lines.back();lines.pop_back();for(int p:e){degree[p]--;through[p].pop_back();}for(int i=0;i<3;i++)for(int j=i+1;j<3;j++){together[e[i]].reset(e[j]);together[e[j]].reset(e[i]);}}
 bool exact_path_dfs(int cur,int target,int depth,int need,std::uint64_t seen)const{
  if(depth==need)return cur==target;
  if(cur==target)return false;
  if(cur<V){for(int id:through[cur]){int nxt=V+id;std::uint64_t bit=std::uint64_t(1)<<nxt;if(seen&bit)continue;if(exact_path_dfs(nxt,target,depth+1,need,seen|bit))return true;}}
  else{for(int nxt:lines[cur-V]){std::uint64_t bit=std::uint64_t(1)<<nxt;if(seen&bit)continue;if(nxt==target&&depth+1!=need)continue;if(exact_path_dfs(nxt,target,depth+1,need,seen|bit))return true;}}
  return false;
 }
 bool old_path6(const Line&e)const{for(int i=0;i<3;i++)for(int j=i+1;j<3;j++)if(exact_path_dfs(e[i],e[j],0,6,std::uint64_t(1)<<e[i]))return true;return false;}
 void collect_halves(int cur,int depth,std::uint64_t mask,std::vector<HalfPath>&out)const{
  if(depth==7){out.push_back({static_cast<unsigned char>(cur),mask});return;}
  if(cur<V){for(int id:through[cur]){int nxt=V+id;std::uint64_t bit=std::uint64_t(1)<<nxt;if(mask&bit)continue;collect_halves(nxt,depth+1,mask|bit,out);}}
  else{for(int nxt:lines[cur-V]){std::uint64_t bit=std::uint64_t(1)<<nxt;if(mask&bit)continue;collect_halves(nxt,depth+1,mask|bit,out);}}
 }
 bool old_path14_pair(int x,int y)const{
  if(degree[x]==0||degree[y]==0)return false;
  // Retain every half-path; these vectors impose no global or per-midpoint
  // capacity.
  std::vector<HalfPath>left,right;left.reserve(192);right.reserve(192);
  collect_halves(x,0,std::uint64_t(1)<<x,left);
  collect_halves(y,0,std::uint64_t(1)<<y,right);
  std::array<std::vector<std::uint64_t>,2*V>masks;
  for(const HalfPath&half:left)masks[half.endpoint].push_back(half.mask);
  for(const HalfPath&half:right){int ep=half.endpoint;std::uint64_t middle=std::uint64_t(1)<<ep;for(std::uint64_t left_mask:masks[ep])if((left_mask&half.mask)==middle)return true;}
  return false;
 }
 bool old_path14(const Line&e)const{for(int i=0;i<3;i++)for(int j=i+1;j<3;j++)if(old_path14_pair(e[i],e[j]))return true;return false;}
 bool bad_pair(const Line&e,int old)const{for(int p:e)if(p<old&&degree[p]>=3)return true;for(int i=0;i<3;i++)for(int j=i+1;j<3;j++)if(e[i]<old&&e[j]<old&&together[e[i]].test(e[j]))return true;return false;}
 void recurse(int p,int lastq,int lastr){
  count.states++;
  while(p<introduced&&degree[p]==3){p++;lastq=lastr=-1;}
  transcript.state(static_cast<std::uint8_t>(p),static_cast<std::uint8_t>(introduced),lastq,lastr,static_cast<std::uint8_t>(lines.size()));
  for(const Line&line:lines)transcript.block(static_cast<std::uint8_t>(line[0]),static_cast<std::uint8_t>(line[1]),static_cast<std::uint8_t>(line[2]));
  if(p>=introduced){
   if(int(lines.size())==introduced){count.completions++;transcript.terminal(0);}
   else transcript.terminal(2);
   transcript.leave();return;
  }
  if(int(lines.size())>=V){transcript.terminal(3);transcript.leave();return;}
  int old=introduced;std::vector<int>values;for(int q=p+1;q<old;q++)if(degree[q]<3&&!together[p].test(q))values.push_back(q);if(old<V)values.push_back(old);if(old+1<V)values.push_back(old+1);
  for(size_t i=0;i<values.size();i++)for(size_t j=i+1;j<values.size();j++){
   int q=values[i],r=values[j];if(r==old+1&&q!=old)continue;if(lastq>=0&&(q<lastq||(q==lastq&&r<=lastr)))continue;
   count.attempted++;Line e{p,q,r};
   if(bad_pair(e,old)){count.pair++;transcript.candidate(static_cast<std::uint8_t>(p),static_cast<std::uint8_t>(q),static_cast<std::uint8_t>(r),transcript_audit::Outcome::degree_or_pair);continue;}
   if(old_path6(e)){count.c8++;transcript.candidate(static_cast<std::uint8_t>(p),static_cast<std::uint8_t>(q),static_cast<std::uint8_t>(r),transcript_audit::Outcome::c8);continue;}
   if(old_path14(e)){count.c16++;transcript.candidate(static_cast<std::uint8_t>(p),static_cast<std::uint8_t>(q),static_cast<std::uint8_t>(r),transcript_audit::Outcome::c16);continue;}
   transcript.candidate(static_cast<std::uint8_t>(p),static_cast<std::uint8_t>(q),static_cast<std::uint8_t>(r),transcript_audit::Outcome::accepted);
   int next=old;if(q==old||r==old)next++;if(r==old+1)next++;int save=introduced;introduced=next;insert(e);recurse(p,q,r);erase();introduced=save;
  }
  transcript.leave();
 }
 Counts run(int orbit){
  transcript.begin(static_cast<std::uint8_t>(V),static_cast<std::uint8_t>(orbit));
  insert({0,1,3});insert({1,2,4});insert({0,2,5});Line first{};
  if(orbit==1){if(V<7){transcript.terminal(4);transcript.leave();return count;}first={0,4,6};introduced=7;}
  else if(orbit==2){if(V<8){transcript.terminal(4);transcript.leave();return count;}first={0,6,7};introduced=8;}
  else{transcript.terminal(4);transcript.leave();return count;}
  insert(first);recurse(1,2,4);return count;
 }
 Counts run_unreduced_root(){transcript.begin(static_cast<std::uint8_t>(V),0);insert({0,1,3});insert({1,2,4});insert({0,2,5});recurse(0,-1,-1);return count;}
 bool transcript_matches_counts()const{return transcript.states()==count.states&&transcript.candidates()==count.attempted;}
};
}
int main(int argc,char**argv){int first=1,last=2;const bool unreduced_root=argc==2&&std::strcmp(argv[1],"--unreduced-root")==0;if(argc==2){if(!unreduced_root){int requested=std::atoi(argv[1]);if(requested<1||requested>2){std::fprintf(stderr,"usage: %s [orbit: 1|2 | --unreduced-root]\n",argv[0]);return 64;}first=last=requested;}}else if(argc!=1){std::fprintf(stderr,"usage: %s [orbit: 1|2 | --unreduced-root]\n",argv[0]);return 64;}auto start=std::chrono::steady_clock::now();triangle_mitm::Counts total;if(unreduced_root){triangle_mitm::Branch b;total=b.run_unreduced_root();if(!b.transcript_matches_counts()){std::fprintf(stderr,"transcript counter mismatch\n");return 70;}std::printf("UNREDUCED_ROOT states=%llu attempted=%llu pair=%llu c8=%llu c16=%llu completions=%llu\n",(unsigned long long)total.states,(unsigned long long)total.attempted,(unsigned long long)total.pair,(unsigned long long)total.c8,(unsigned long long)total.c16,(unsigned long long)total.completions);std::printf("TRANSCRIPT orbit=0 states=%llu candidates=%llu sha256=%s\n",(unsigned long long)b.transcript.states(),(unsigned long long)b.transcript.candidates(),b.transcript.hex_digest().c_str());std::fflush(stdout);}else for(int o=first;o<=last;o++){triangle_mitm::Branch b;auto c=b.run(o);if(!b.transcript_matches_counts()){std::fprintf(stderr,"transcript counter mismatch in orbit %d\n",o);return 70;}total+=c;std::printf("ORBIT %d states=%llu attempted=%llu pair=%llu c8=%llu c16=%llu completions=%llu\n",o,(unsigned long long)c.states,(unsigned long long)c.attempted,(unsigned long long)c.pair,(unsigned long long)c.c8,(unsigned long long)c.c16,(unsigned long long)c.completions);std::printf("TRANSCRIPT orbit=%d states=%llu candidates=%llu sha256=%s\n",o,(unsigned long long)b.transcript.states(),(unsigned long long)b.transcript.candidates(),b.transcript.hex_digest().c_str());std::fflush(stdout);}double sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();std::printf("TOTAL V=%d states=%llu attempted=%llu pair=%llu c8=%llu c16=%llu completions=%llu seconds=%.6f\n",triangle_mitm::V,(unsigned long long)total.states,(unsigned long long)total.attempted,(unsigned long long)total.pair,(unsigned long long)total.c8,(unsigned long long)total.c16,(unsigned long long)total.completions,sec);return total.completions?2:0;}
