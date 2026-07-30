#!/usr/bin/env python3
"""Independent verifier for the six triangle-rooted cap-29 terminal kernels.

The verifier does not call NetworkX or a graph-isomorphism package.  It
checks explicit point and block bijections from every one of the 337 depth-19
states to one of six representatives, and then checks directly that no
representative admits another block on its 29-point set without creating C4,
C8, or C16.
"""
from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from pathlib import Path

NPOINTS = 29
NBLOCKS = 19
EXPECTED_CLASS_SIZES = {1: 2, 2: 20, 3: 20, 4: 75, 5: 200, 6: 20}
EXPECTED_COMPATIBLE = {
    1: {(12,21),(12,22),(15,23),(15,24),(16,25),(16,26)},
    2: {(11,21),(12,22),(12,23),(15,16),(15,17)},
    3: {(11,13),(16,24),(16,25),(17,26),(17,27)},
    4: {(11,12),(11,13),(16,17),(16,18)},
    5: {(12,13),(12,14)},
    6: {(12,13),(12,14)},
}


def parse_blocks(payload: str) -> list[tuple[int,int,int]]:
    blocks=[]
    for token in payload.split(';'):
        if not token:
            continue
        block=tuple(map(int,token.split(',')))
        if len(block)!=3 or tuple(sorted(block))!=block:
            raise ValueError(f"bad block {token!r}")
        blocks.append(block)
    return blocks


def load_states(path: Path):
    states=[]
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        head,payload=line.split(' ',5)[:5],line.split(' ',5)[5]
        serial,orbit,local,intro,point=map(int,head)
        if serial!=len(states):
            raise ValueError("state serials are not consecutive")
        blocks=parse_blocks(payload)
        states.append((orbit,local,intro,point,blocks))
    return states


def load_mappings(path: Path):
    rows=[]
    for line in path.read_text().splitlines():
        if not line or line.startswith('#'):
            continue
        values=list(map(int,line.split()))
        expected=4+NPOINTS+NBLOCKS
        if len(values)!=expected:
            raise ValueError(f"mapping row has {len(values)} integers, expected {expected}")
        serial,orbit,local,klass=values[:4]
        rows.append((serial,orbit,local,klass,values[4:4+NPOINTS],values[4+NPOINTS:]))
    return rows


def incidence_data(blocks):
    degree=[0]*NPOINTS
    incident=[[] for _ in range(NPOINTS)]
    paired=set()
    for i,b in enumerate(blocks):
        if len(set(b))!=3 or any(x<0 or x>=NPOINTS for x in b):
            raise ValueError("invalid point in block")
        for x in b:
            degree[x]+=1
            incident[x].append(i)
        for x,y in itertools.combinations(b,2):
            key=tuple(sorted((x,y)))
            if key in paired:
                raise ValueError("nonlinear representative")
            paired.add(key)
    if max(degree)>3:
        raise ValueError("degree exceeds three")
    return degree,incident,paired


def path_witness(blocks,incident,start,target,length):
    """Return a simple alternating incidence path, or None."""
    seen={('p',start)}
    path=[('p',start)]
    def dfs(kind,index,depth):
        if depth==length:
            return list(path) if kind=='p' and index==target else None
        if kind=='p' and index==target:
            return None
        if kind=='p':
            next_vertices=[('b',b) for b in incident[index]]
        else:
            next_vertices=[('p',p) for p in blocks[index]]
        for nxt in next_vertices:
            if nxt in seen:
                continue
            if nxt==('p',target) and depth+1!=length:
                continue
            seen.add(nxt); path.append(nxt)
            answer=dfs(nxt[0],nxt[1],depth+1)
            if answer is not None:
                return answer
            path.pop(); seen.remove(nxt)
        return None
    return dfs('p',start,0)


def verify_mapping(state_blocks,rep_blocks,point_map,block_map):
    if sorted(point_map)!=list(range(NPOINTS)):
        raise ValueError("point map is not a permutation")
    if sorted(block_map)!=list(range(NBLOCKS)):
        raise ValueError("block map is not a permutation")
    for i,b in enumerate(state_blocks):
        image=tuple(sorted(point_map[x] for x in b))
        if image!=tuple(rep_blocks[block_map[i]]):
            raise ValueError(f"incidence mapping fails at block {i}")


def verify_kernel(klass,blocks):
    if len(blocks)!=NBLOCKS:
        raise ValueError("representative does not have 19 blocks")
    degree,incident,paired=incidence_data(blocks)
    boundary=[x for x,d in enumerate(degree) if d<3]
    compatible=set()
    blocked=Counter()
    for x,y in itertools.combinations(boundary,2):
        key=(x,y)
        if key in paired:
            blocked['C4']+=1
            continue
        if path_witness(blocks,incident,x,y,6) is not None:
            blocked['C8']+=1
            continue
        if path_witness(blocks,incident,x,y,14) is not None:
            blocked['C16']+=1
            continue
        compatible.add(key)
    if compatible!=EXPECTED_COMPATIBLE[klass]:
        raise ValueError(
            f"class {klass} compatible edges differ: {sorted(compatible)}")
    for triple in itertools.combinations(boundary,3):
        if all(tuple(sorted(pair)) in compatible for pair in itertools.combinations(triple,2)):
            raise ValueError(f"class {klass} compatible graph has triangle {triple}")
    return boundary,blocked,compatible


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('representatives',type=Path)
    parser.add_argument('states',type=Path)
    parser.add_argument('mappings',type=Path)
    args=parser.parse_args()

    raw=json.loads(args.representatives.read_text())
    reps={int(entry['class']):[tuple(x) for x in entry['blocks']] for entry in raw}
    if set(reps)!=set(EXPECTED_CLASS_SIZES):
        raise ValueError("wrong representative class set")
    states=load_states(args.states)
    mappings=load_mappings(args.mappings)
    if len(states)!=337 or len(mappings)!=337:
        raise ValueError("expected exactly 337 states and mappings")

    used=Counter()
    for idx,(state,mapping) in enumerate(zip(states,mappings)):
        orbit,local,intro,point,blocks=state
        serial,mo,ml,klass,point_map,block_map=mapping
        if serial!=idx or (orbit,local)!=(mo,ml):
            raise ValueError("mapping/state identity mismatch")
        if intro!=NPOINTS or len(blocks)!=NBLOCKS:
            raise ValueError("depth-19 state has wrong size")
        verify_mapping(blocks,reps[klass],point_map,block_map)
        used[klass]+=1
    if dict(used)!=EXPECTED_CLASS_SIZES:
        raise ValueError(f"class multiplicities differ: {dict(used)}")

    print("VERIFIED: 337 depth-19 states map to six color-preserving kernels.")
    for klass in sorted(reps):
        boundary,blocked,compatible=verify_kernel(klass,reps[klass])
        print(
            f"K{klass}: multiplicity={used[klass]} boundary={len(boundary)} "
            f"blocked(C4,C8,C16)=({blocked['C4']},{blocked['C8']},{blocked['C16']}) "
            f"compatible={sorted(compatible)}")
    print(
        "VERIFIED: every compatible-pair graph is triangle-free; "
        "no kernel admits a new block within cap 29."
    )

if __name__=='__main__':
    main()
