"""
 Models for openletsweb
"""

from django.db import models
from django.contrib.sites.models import Site
from django.contrib.auth.models import User


class Content(models.Model):
	"""A semi-static piece of content. Used for Contact, About, and
	the homepage pitch.
	"""

	name = models.CharField(max_length=30)
	time_updated = models.DateTimeField(auto_now=True)
	body = models.TextField()
	author = models.ForeignKey(User)
	site = models.ForeignKey(Site)

	def __unicode__(self):
		return '%s for %s' % (self.name, self.site)

class NewsPost(models.Model):
	"""A news post."""

	title = models.CharField(max_length=150)
	time_created = models.DateTimeField(auto_now_add=True)
	time_updated = models.DateTimeField(auto_now=True)
	body = models.TextField()
	author = models.ForeignKey(User)
	site = models.ForeignKey(Site)

	def __unicode__(self):
		return 'News Post: %s posted %s for %s' % (self.title, self.time_created, self.site)
