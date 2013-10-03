#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Mike Sheldon <elleo@gnu.org>
# 
# This program is free software: you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. 
# 
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details. 
# 
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from PySide import QtCore


class App(QtCore.QObject):


	def __init__(self, appId, appName, appCompany, appIndex):
		self.appId = appId
		self.appName = appName
		self.appCompany = appCompany
		self.appIndex = appIndex


class AppListModel(QtCore.QAbstractListModel):


	APPID_ROLE = QtCore.Qt.UserRole + 1
	APPNAME_ROLE = QtCore.Qt.UserRole + 2
	APPCOMPANY_ROLE = QtCore.Qt.UserRole + 3
	APPINDEX_ROLE = QtCore.Qt.UserRole + 4


	def __init__(self, parent=None):
		super(AppListModel, self).__init__(parent)
		self._data = []
		keys = {}
		keys[AppListModel.APPID_ROLE] = 'appId'
		keys[AppListModel.APPNAME_ROLE] = 'appName'
		keys[AppListModel.APPCOMPANY_ROLE] = 'appCompany'
		keys[AppListModel.APPINDEX_ROLE] = 'appIndex'
		self.setRoleNames(keys)


	def rowCount(self, index):
		return len(self._data)


	def data(self, index, role):
		app = self._data[index.row()]

		if role == AppListModel.APPID_ROLE:
			return app.appId
		elif role == AppListModel.APPNAME_ROLE:
			return app.appName
		elif role == AppListModel.APPCOMPANY_ROLE:
			return app.appCompany
		elif role == AppListModel.APPINDEX_ROLE:
			return app.appIndex
		else:
			return None


	def add(self, app):
		self.beginInsertRows(QtCore.QModelIndex(), 0, 0) #notify view about upcoming change        
		self._data.insert(0, app)
		self.endInsertRows() #notify view that change happened


	def addToEnd(self, app):
		count = len(self._data)
		self.beginInsertRows(QtCore.QModelIndex(), count, count)
		self._data.insert(count, app)
		self.endInsertRows()


	def getIndex(self, appid):
		for app in self._data:
			if app.appid == appid:
				return self._data.index(app)

		return None


	def clear(self):
		self.beginRemoveRows(QtCore.QModelIndex(), 0, len(self._data) - 1)
		self._data = []
		self.endRemoveRows()


	def setData(self, index, value, role):
		# dataChanged signal isn't obeyed by ListView (QTBUG-13664)
		# so work around it by removing then re-adding rows
		self.beginRemoveRows(QtCore.QModelIndex(), index, index)
		app = self._data.pop(index)
		self.endRemoveRows()
		self.beginInsertRows(QtCore.QModelIndex(), index, index)
		if role == AppListModel.FAVOURITE_ROLE:
			app.favourite = value
		elif role == AppListModel.FOLLOWING_ROLE:
			app.following = value
		self._data.insert(index, app)
		self.endInsertRows()


if __name__ == "__main__":
	StatusNetMeego()
