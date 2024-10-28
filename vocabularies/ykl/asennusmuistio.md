### Päivitys 28.10.2024
```
> dos2unix ykl-tbc.ttl
> cp -p ykl-tbc.ttl ykl-tbc-validoitu.ttl
> riot --validate ykl-tbc-validoitu.ttl
> cp -p ykl-tbc-validoitu.ttl ykl-tbc-skossattava.ttl
```
EDIT: toskos.sh: RAWFILE="ykl-tbc-skossattava.ttl"
```
> . /venvs/python3/bin/activate
> ./toskos.sh
> s-delete http://localhost:3030/skosmos/data http://urn.fi/URN:NBN:fi:au:ykl:
> s-put http://localhost:3030/skosmos/data http://urn.fi/URN:NBN:fi:au:ykl: ykl-skos.ttl
```
CHECK: \ 
- 78.89114 Punk rock \
- Hardcore punk \
- koneoppiminen (61+) \
- kalliomekaniikka (66.2)
```
> git pull / commit / push
```
