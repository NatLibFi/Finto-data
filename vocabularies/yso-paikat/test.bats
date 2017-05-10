#!/usr/bin/env bats

setup() {
  make -s pl.nt
}

@test "Hietalahti (Helsinki)" {
  grep "Hietalahti (Helsinki)" pl.nt
  ! grep "Helsinki (Hietalahti)" pl.nt
}

@test "Taivallahti (Helsinki)" {
  grep "Taivallahti (Helsinki)" pl.nt
  ! grep "Helsinki (Taivallahti)" pl.nt
}

@test "Töölönlahti (Helsinki)" {
  grep "Töölönlahti (Helsinki)" pl.nt
  ! grep "Helsinki (Töölönlahti)" pl.nt
}

@test "Barönsalmi (Inkoo)" {
  grep "Barönsalmi (Inkoo)" pl.nt
  ! grep "Inkoo (Barönsalmi)" pl.nt
}

@test "Linnunlahti (Joensuu)" {
  grep "Linnunlahti (Joensuu)" pl.nt
  ! grep "Joensuu (Linnunlahti)" pl.nt
}

@test "Kellolahti (Kaavi)" {
  grep "Kellolahti (Kaavi)" pl.nt
  ! grep "Kaavi (Kellolahti)" pl.nt
}

@test "Säynätlahti (Kuhmoinen)" {
  grep "Säynätlahti (Kuhmoinen)" pl.nt
  ! grep "Kuhmoinen (Säynätlahti)" pl.nt
}

@test "Kirkkosalmi (Parainen)" {
  grep "Kirkkosalmi (Parainen)" pl.nt
  ! grep "Parainen (Kirkkosalmi)" pl.nt
}

@test "Sipoonlahti (Sipoo)" {
  grep "Sipoonlahti (Sipoo)" pl.nt
  ! grep "Sipoo (Sipoonlahti)" pl.nt
}

@test "Sätöslahti (Viinijärvi)" {
  grep "Sätöslahti (Viinijärvi)" pl.nt
  ! grep "Viinijärvi (Sätöslahti)" pl.nt
}

@test "Pitkäkoski (Helsinki)" {
  grep "Pitkäkoski (Helsinki)" pl.nt
  ! grep "Helsinki (Pitkäkoski)" pl.nt
}

@test "Vaajakoski (Jyväskylän maalaiskunta)" {
  grep "Vaajakoski (Jyväskylän maalaiskunta)" pl.nt
  ! grep '"Jyväskylän maalaiskunta (Vaajakoski)"' pl.nt
}

@test "Vallinkoski (koski, Imatra)" {
  grep "Vallinkoski (koski, Imatra)" pl.nt
  ! grep "Vallinkoski (koski) (Imatra)" pl.nt
}

@test "ei Helsinki-alkuisia joissa sulkutarkenne" {
  ! grep 'Helsinki (' pl.nt
}

@test "ei ketjuja labeleissa" {
  ! grep ' -- ' pl.nt | grep -v 'core#note'
}

@test "ei samannimisiä paikkoja" {
  dups="$(grep 'core#prefLabel' pl.nt | cut -d ' ' -f 3- | sort | uniq -d)"
  echo $dups
  [ "$dups" = "" ]

}
