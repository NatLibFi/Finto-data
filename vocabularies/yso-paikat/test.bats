#!/usr/bin/env bats

setup() {
  make -s yso-paikat.nt
}

@test "Hietalahti (Helsinki)" {
  grep "Hietalahti (Helsinki)" yso-paikat.nt
  ! grep "Helsinki (Hietalahti)" yso-paikat.nt
}

@test "Taivallahti (Helsinki)" {
  grep "Taivallahti (Helsinki)" yso-paikat.nt
  ! grep "Helsinki (Taivallahti)" yso-paikat.nt
}

@test "Töölönlahti (Helsinki)" {
  grep "Töölönlahti (Helsinki)" yso-paikat.nt
  ! grep "Helsinki (Töölönlahti)" yso-paikat.nt
}

@test "Barönsalmi (Inkoo)" {
  grep "Barönsalmi (Inkoo)" yso-paikat.nt
  ! grep "Inkoo (Barönsalmi)" yso-paikat.nt
}

@test "Linnunlahti (Joensuu)" {
  grep "Linnunlahti (Joensuu)" yso-paikat.nt
  ! grep "Joensuu (Linnunlahti)" yso-paikat.nt
}

@test "Kellolahti (Kaavi)" {
  grep "Kellolahti (Kaavi)" yso-paikat.nt
  ! grep "Kaavi (Kellolahti)" yso-paikat.nt
}

@test "Säynätlahti (Kuhmoinen)" {
  grep "Säynätlahti (Kuhmoinen)" yso-paikat.nt
  ! grep "Kuhmoinen (Säynätlahti)" yso-paikat.nt
}

@test "Kirkkosalmi (Parainen)" {
  grep "Kirkkosalmi (Parainen)" yso-paikat.nt
  ! grep "Parainen (Kirkkosalmi)" yso-paikat.nt
}

@test "Sipoonlahti (Sipoo)" {
  grep "Sipoonlahti (Sipoo)" yso-paikat.nt
  ! grep "Sipoo (Sipoonlahti)" yso-paikat.nt
}

@test "Sätöslahti (Viinijärvi)" {
  grep "Sätöslahti (Viinijärvi)" yso-paikat.nt
  ! grep "Viinijärvi (Sätöslahti)" yso-paikat.nt
}

@test "Pitkäkoski (Vantaa)" {
  grep "Pitkäkoski (Vantaa)" yso-paikat.nt
  ! grep "Helsinki (Pitkäkoski)" yso-paikat.nt
  ! grep "Vantaa (Pitkäkoski)" yso-paikat.nt
}

@test "Vaajakoski (Jyväskylän maalaiskunta)" {
  grep "Vaajakoski (Jyväskylän maalaiskunta)" yso-paikat.nt
  ! grep '"Jyväskylän maalaiskunta (Vaajakoski)"' yso-paikat.nt
}

@test "Vallinkoski (Imatra : koski)" {
  grep "Vallinkoski (Imatra : koski)" yso-paikat.nt
  ! grep "Vallinkoski (koski) (Imatra)" yso-paikat.nt
}

@test "Isojärvi (Multia : järvi)" {
  grep "Isojärvi (Multia : järvi)" yso-paikat.nt
  ! grep '"Isojärvi (Multia)"@fi' yso-paikat.nt
}

@test "Isojärvi (Multia : kylä)" {
  grep "Isojärvi (Multia : kylä)" yso-paikat.nt
  ! grep '"Isojärvi (Multia)"@fi' yso-paikat.nt
}

@test "ei Helsinki-alkuisia joissa sulkutarkenne" {
  ! grep 'Helsinki (' yso-paikat.nt
}

@test "ei Karjalan tasavalta -alkuisia joissa sulkutarkenne" {
  ! grep 'Karjalan tasavalta (' yso-paikat.nt
}

@test "ei Kiihtelysvaara-alkuisia joissa sulkutarkenne" {
  ! grep 'Kiihtelysvaara (' yso-paikat.nt
}

@test "ei Loviisa-alkuisia joissa sulkutarkenne" {
  ! grep 'Loviisa (' yso-paikat.nt
}

@test "ei Pohjanmaa-alkuisia joissa sulkutarkenne" {
  ! grep 'Pohjanmaa (' yso-paikat.nt
}

@test "ei Uuras-alkuisia joissa sulkutarkenne" {
  ! grep 'Uuras (' yso-paikat.nt
}

@test "ei Yhdysvallat-alkuisia joissa sulkutarkenne" {
  ! grep 'Yhdysvallat (' yso-paikat.nt
}

@test "ei ketjuja labeleissa" {
  ! grep 'core#prefLabel.* -- ' yso-paikat.nt
}

@test "ei ketjuja huomautuksissa" {
  ! grep 'core#note.* -- ' yso-paikat.nt
}

@test "ei samannimisiä paikkoja" {
  dups="$(grep 'core#prefLabel' yso-paikat.nt | cut -d ' ' -f 3- | sort | uniq -d)"
  echo $dups
  [ "$dups" = "" ]

}

@test "ei pareja, joista vain toisella on tarkenne" {
  grep 'core#prefLabel' yso-paikat.nt | grep ' : ' | cut -d ' ' -f 3- | sed -e 's/ : [^)]*)/)/' >undisambiguated.txt
  ! grep -F -f undisambiguated.txt yso-paikat.nt
}

@test "ei kielikoodittomia labeleita" {
  nolang="$(grep 'core#prefLabel' yso-paikat.nt | cut -d ' ' -f 3- | grep -v '@')"
  echo $nolang
  [ "$nolang" = "" ]
}
