all: tgl-gen.fst tgl-morph.fst tgl-ceb.automorf.hfst ceb-gen.fst ceb-morph.fst

tgl-lexc.fst: tgl.lexc
	hfst-lexc tgl.lexc -o $@

tgl-twol.fst: tgl.twol
	hfst-twolc tgl.twol -o $@

tgl-gen.fst: tgl-lexc.fst tgl-twol.fst 
	hfst-compose-intersect -l tgl-lexc.fst tgl-twol.fst -o $@

tgl-morph.fst: tgl-gen.fst
	hfst-invert tgl-gen.fst > $@

ceb-lexc.fst: ceb.lexc
	hfst-lexc ceb.lexc -o $@

ceb-twol.fst: ceb.twol
	hfst-twolc ceb.twol -o $@

ceb-gen.fst: ceb-lexc.fst ceb-twol.fst 
	hfst-compose-intersect -l ceb-lexc.fst ceb-twol.fst -o $@

ceb-morph.fst: ceb-gen.fst
	hfst-invert ceb-gen.fst > $@

tgl-ceb.automorf.hfst: tgl-morph.fst 
	cat tgl-gen.fst | hfst-substitute -F tgl.relabel  > $@.tmp
	hfst-invert $@.tmp > $@.tmp1
	hfst-lookup-optimize $@.tmp1 -o $@
	rm $@.tmp $@.tmp1
	

clean: 
	rm tgl-ceb.automorf.hfst tgl-gen.fst tgl-morph.fst tgl-twol.fst tgl-lexc.fst
	rm ceb-gen.fst ceb-morph.fst ceb-twol.fst ceb-lexc.fst
