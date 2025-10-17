import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
  id: row
  spacing: 8

  property alias titleText: titleLabel.text
  property alias valueText: valueLabel.text
  property alias titleColor: titleLabel.color
  property alias valueColor: valueLabel.color
  property alias valueWrapMode: valueLabel.wrapMode
  property alias valueElide: valueLabel.elide
  property alias valueFont: valueLabel.font


  InfoTitleLabel { id: titleLabel }
  InfoValueLabel { id: valueLabel }
}
