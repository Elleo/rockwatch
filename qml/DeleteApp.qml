import QtQuick 1.1;
import Qt.labs.components 1.0;
import com.nokia.meego 1.0;
import com.nokia.extras 1.0;

import QtMobility.gallery 1.1;

Page {
	id: deleteApp;
	tools: ToolBarLayout {
		id: tools;
		ToolButton {
			width: 64;
			height: 64;
			iconSource: "image://theme/icon-m-toolbar-back-white";
			onClicked: { 
				pageStack.pop(); 
				tools.visible = false;
			}
		}
	}

	ListView {
		anchors.fill: parent;
		model: appListModel;
		delegate: appDelegate;
	}

	Component {
		id: appDelegate;

		Item {
			height: 72;
			width: parent.width;
			MouseArea {
				anchors.fill: parent

				Image {
					id: appIcon;
					source: "image://theme/icon-m-toolbar-close-white";
					height: 64;
					fillMode: Image.PreserveAspectFit;
					smooth: true;
				}

				Column {
					height: parent.height;
					width: parent.width - appIcon.width;
					anchors.left: appIcon.right;
					anchors.leftMargin: 10;

					Label {
						text: appName;
						font.pointSize: 24;
						font.bold: true;
						elide: Text.ElideRight;
					}

					Label {
						text: appCompany;
						font.pointSize: 12;
						elide: Text.ElideRight;
					}
				}

				onClicked: {
					delMessage.titleText = "Delete " + appName;
					delMessage.message = "Are you sure you want to remove " + appName + " from your watch?";
					rootWin.appId = appId;
					rootWin.appIndex = appIndex;
					delMessage.open();
				}
			}
		}

	}

	QueryDialog {
		id: delMessage;
		acceptButtonText: "Delete";
		rejectButtonText: "Cancel";
		onAccepted: {
			console.log("Deleting app: " + rootWin.appId + ", index: " + rootWin.appIndex);
			rootWin.deleteApp(rootWin.appId, rootWin.appIndex);
		}
	}

}
