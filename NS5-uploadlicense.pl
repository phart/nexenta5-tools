#!/usr/bin/perl -w
use strict;
use JSON::Tiny  qw(decode_json encode_json);;


my $username = "admin";
my $password = "nexentA01";
my $server_addr = "172.16.251.135:8443";
my $header = q[-s -k -H "Accept: application/json" -H "Content-Type: application/json"];


sub setup_auth {

  my ($username,$password,$server_addr,$header) = @_;

  my $bytes = encode_json {username => $username, password => $password};

  my $cmd = qq[curl $header -X POST -d '$bytes' https://$server_addr/auth/login];
  my $string = `$cmd`;
  my $hash = decode_json($string);
  my $token = $$hash{token};

  $header = qq[ -H "Authorization: Bearer $token" ];

  return $header;

}

$header = setup_auth($username,$password,$server_addr,$header);


#my $upload_license = qq[curl $header -X POST -F license=\@LicenseContent_09Oct2017_04-29-17_PM.txt https://$server_addr/settings/license];

my $upload_license = qq[curl $header -s -k -F license=\@LicenseContent_09Oct2017_04-29-17_PM.txt https://$server_addr/settings/license];

print `$upload_license`;

