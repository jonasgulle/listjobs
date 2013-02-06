use strict;
use vars qw($VERSION %IRSSI);

use Irssi;
use XML::XPath;
use LWP::Simple;

###############################################################################
# CONFIGURATION VALUES - Modify if neccessary.
###############################################################################
# The URL to the RSS-feed.
my $urlfeed = 'http://source.jobvite.com/TalentNetwork/action/feed/v1/job?c=qV49VfwN';
###############################################################################

$VERSION = '1.00';
%IRSSI = (
	authors     => 'Jonas Gulle',
	contact     => 'jonas.gulle@gmail.com',
	name        => 'listjobs',
	description => 'Exclusively made for AndreMploy',
	licence     => 'Public Domain',
	url         => 'http://github.com/jonasgulle/listjobs'
);

sub get_job_feed {
	my ($limit) = @_;
	my @jobs;

	my $num_jobs = 0;
	my $xp = XML::XPath->new(xml => get $urlfeed);
	my $stories = $xp->find('rss/channel/item');
	foreach my $story($stories->get_nodelist) {
		my $url = $xp->find('link', $story)->string_value;
		my $title = $xp->find('title', $story)->string_value;
		push @jobs, {url => "$url", title => "$title"};
		if (($limit) and ($limit == ++$num_jobs)) {
			return @jobs;
		}
	}

	return @jobs;
}

sub sig_listjobs {
	my ($server, $msg, $nick, $nick_addr, $target) = @_;

	if ($msg ne '!listjobs') {
		return;
	}

	my @jobs = get_job_feed();
	$server->command("msg $nick $_->{title} ($_->{url})") foreach (@jobs);
}

sub sig_latestjobs {
	my ($server, $msg, $nick, $nick_addr, $target) = @_;

	if ($msg ne '!latestjobs') {
		return;
	}

	my @jobs = get_job_feed(10);
	$server->command("msg $nick $_->{title} ($_->{url})") foreach (@jobs);
}

Irssi::signal_add 'message public', 'sig_listjobs';
Irssi::signal_add 'message public', 'sig_latestjobs';

