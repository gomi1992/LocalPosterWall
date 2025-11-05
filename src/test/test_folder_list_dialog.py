"""
FolderListDialog 测试模块

本模块包含对FolderListDialog类的单元测试，测试内容包括：
- 对话框初始化测试
- UI组件创建测试
- 添加文件夹功能测试
- 删除文件夹功能测试
- 文件夹验证测试
- 重复检查测试
- 用户确认和取消操作测试
- 异常处理测试

使用unittest框架和PySide6测试工具进行测试，模拟用户交互。
"""

import unittest
import os
import sys
from pathlib import Path
from unittest import mock

from PySide6.QtWidgets import QApplication, QMessageBox, QFileDialog
from PySide6.QtCore import Qt

# 导入被测试模块
from src.folder_list_dialog import FolderListDialog


class TestFolderListDialog(unittest.TestCase):
    """FolderListDialog类的单元测试"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化：创建QApplication实例"""
        # 确保只创建一个QApplication实例
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """每个测试用例执行前的设置"""
        # 创建测试用的临时文件夹路径
        self.test_folder1 = str(Path(__file__).parent / "test_movies1")
        self.test_folder2 = str(Path(__file__).parent / "test_movies2")
        self.test_folder3 = str(Path(__file__).parent / "test_movies3")
        
        # 创建实际的测试文件夹
        Path(self.test_folder1).mkdir(exist_ok=True)
        Path(self.test_folder2).mkdir(exist_ok=True)
        
        # 初始文件夹列表
        self.initial_folders = [self.test_folder1, self.test_folder2]

    def tearDown(self):
        """每个测试用例执行后的清理"""
        # 清理测试文件夹
        for folder in [self.test_folder1, self.test_folder2, self.test_folder3]:
            folder_path = Path(folder)
            if folder_path.exists():
                try:
                    folder_path.rmdir()
                except:
                    pass

    def test_initialization(self):
        """测试对话框初始化"""
        dialog = FolderListDialog(self.initial_folders)
        
        # 验证窗口标题
        self.assertEqual(dialog.windowTitle(), '管理电影文件夹')
        
        # 验证是否为模态对话框
        self.assertTrue(dialog.isModal())
        
        # 验证最小尺寸
        self.assertGreaterEqual(dialog.minimumWidth(), 500)
        self.assertGreaterEqual(dialog.minimumHeight(), 400)
        
        # 验证初始文件夹列表
        self.assertEqual(len(dialog.folders), 2)
        self.assertIn(self.test_folder1, dialog.folders)
        self.assertIn(self.test_folder2, dialog.folders)

    def test_initialization_with_empty_folders(self):
        """测试使用空文件夹列表初始化"""
        dialog = FolderListDialog([])
        
        # 验证文件夹列表为空
        self.assertEqual(len(dialog.folders), 0)
        self.assertEqual(dialog.list_widget.count(), 0)

    def test_initialization_with_none_folders(self):
        """测试使用None初始化"""
        dialog = FolderListDialog(None)
        
        # 验证文件夹列表为空
        self.assertEqual(len(dialog.folders), 0)
        self.assertEqual(dialog.list_widget.count(), 0)

    def test_ui_components_created(self):
        """测试UI组件是否正确创建"""
        dialog = FolderListDialog(self.initial_folders)
        
        # 验证列表组件存在
        self.assertIsNotNone(dialog.list_widget)
        self.assertEqual(dialog.list_widget.count(), 2)
        
        # 验证按钮组存在
        self.assertIsNotNone(dialog.button_box)
        
        # 验证列表项内容
        item_texts = [dialog.list_widget.item(i).text() 
                      for i in range(dialog.list_widget.count())]
        self.assertIn(self.test_folder1, item_texts)
        self.assertIn(self.test_folder2, item_texts)

    def test_get_folders(self):
        """测试获取文件夹列表功能"""
        dialog = FolderListDialog(self.initial_folders)
        
        folders = dialog.get_folders()
        
        # 验证返回的是副本而非原始列表
        self.assertIsNot(folders, dialog.folders)
        
        # 验证内容相同
        self.assertEqual(folders, self.initial_folders)

    @mock.patch('src.folder_list_dialog.QFileDialog.getExistingDirectory')
    @mock.patch('src.folder_list_dialog.QMessageBox.information')
    def test_add_folder_success(self, mock_msgbox, mock_file_dialog):
        """测试成功添加文件夹"""
        dialog = FolderListDialog([self.test_folder1])
        
        # 创建新的测试文件夹
        Path(self.test_folder3).mkdir(exist_ok=True)
        
        # 模拟用户选择文件夹
        mock_file_dialog.return_value = self.test_folder3
        
        # 执行添加操作
        dialog.add_folder()
        
        # 验证文件夹已添加
        self.assertIn(self.test_folder3, dialog.folders)
        self.assertEqual(len(dialog.folders), 2)
        self.assertEqual(dialog.list_widget.count(), 2)
        
        # 验证显示了成功消息
        mock_msgbox.assert_called_once()

    @mock.patch('src.folder_list_dialog.QFileDialog.getExistingDirectory')
    def test_add_folder_cancelled(self, mock_file_dialog):
        """测试取消添加文件夹"""
        dialog = FolderListDialog([self.test_folder1])
        
        # 模拟用户取消选择
        mock_file_dialog.return_value = ''
        
        initial_count = len(dialog.folders)
        
        # 执行添加操作
        dialog.add_folder()
        
        # 验证文件夹列表未改变
        self.assertEqual(len(dialog.folders), initial_count)

    @mock.patch('src.folder_list_dialog.QFileDialog.getExistingDirectory')
    @mock.patch('src.folder_list_dialog.QMessageBox.warning')
    def test_add_nonexistent_folder(self, mock_msgbox, mock_file_dialog):
        """测试添加不存在的文件夹"""
        dialog = FolderListDialog([self.test_folder1])
        
        # 模拟选择不存在的文件夹
        nonexistent_folder = str(Path(__file__).parent / "nonexistent_folder")
        mock_file_dialog.return_value = nonexistent_folder
        
        # 执行添加操作
        dialog.add_folder()
        
        # 验证文件夹未添加
        self.assertNotIn(nonexistent_folder, dialog.folders)
        
        # 验证显示了警告消息
        mock_msgbox.assert_called_once()

    @mock.patch('src.folder_list_dialog.QFileDialog.getExistingDirectory')
    @mock.patch('src.folder_list_dialog.QMessageBox.information')
    def test_add_duplicate_folder(self, mock_msgbox, mock_file_dialog):
        """测试添加重复的文件夹"""
        dialog = FolderListDialog([self.test_folder1])
        
        # 模拟选择已存在的文件夹
        mock_file_dialog.return_value = self.test_folder1
        
        initial_count = len(dialog.folders)
        
        # 执行添加操作
        dialog.add_folder()
        
        # 验证文件夹未重复添加
        self.assertEqual(len(dialog.folders), initial_count)
        self.assertEqual(dialog.folders.count(self.test_folder1), 1)
        
        # 验证显示了提示消息
        mock_msgbox.assert_called_once()

    @mock.patch('src.folder_list_dialog.QFileDialog.getExistingDirectory')
    @mock.patch('src.folder_list_dialog.QMessageBox.warning')
    def test_add_empty_path(self, mock_msgbox, mock_file_dialog):
        """测试添加空路径"""
        dialog = FolderListDialog([self.test_folder1])
        
        # 模拟返回空字符串（已在取消测试中处理）和空白字符串
        for empty_path in ['   ', '\t', '\n']:
            mock_file_dialog.return_value = empty_path
            initial_count = len(dialog.folders)
            
            dialog.add_folder()
            
            # 验证空路径未添加
            self.assertEqual(len(dialog.folders), initial_count)

    def test_remove_folder_success(self):
        """测试成功删除文件夹"""
        dialog = FolderListDialog(self.initial_folders.copy())
        
        # 选择第一个项目
        dialog.list_widget.setCurrentRow(0)
        
        # 执行删除操作
        dialog.remove_folder()
        
        # 验证文件夹已删除
        self.assertEqual(len(dialog.folders), 1)
        self.assertNotIn(self.test_folder1, dialog.folders)
        self.assertEqual(dialog.list_widget.count(), 1)

    @mock.patch('src.folder_list_dialog.QMessageBox.information')
    def test_remove_folder_no_selection(self, mock_msgbox):
        """测试未选择项目时删除文件夹"""
        dialog = FolderListDialog(self.initial_folders.copy())
        
        # 不选择任何项目
        dialog.list_widget.setCurrentRow(-1)
        
        initial_count = len(dialog.folders)
        
        # 执行删除操作
        dialog.remove_folder()
        
        # 验证文件夹列表未改变
        self.assertEqual(len(dialog.folders), initial_count)
        
        # 验证显示了提示消息
        mock_msgbox.assert_called_once()

    def test_remove_all_folders(self):
        """测试删除所有文件夹"""
        dialog = FolderListDialog(self.initial_folders.copy())
        
        # 逐个删除所有文件夹
        while dialog.list_widget.count() > 0:
            dialog.list_widget.setCurrentRow(0)
            dialog.remove_folder()
        
        # 验证所有文件夹已删除
        self.assertEqual(len(dialog.folders), 0)
        self.assertEqual(dialog.list_widget.count(), 0)

    def test_validate_folder_valid(self):
        """测试验证有效的文件夹"""
        dialog = FolderListDialog([])
        
        # 验证已存在的文件夹
        result = dialog._validate_folder(self.test_folder1)
        self.assertTrue(result)

    @mock.patch('src.folder_list_dialog.QMessageBox.warning')
    def test_validate_folder_empty(self, mock_msgbox):
        """测试验证空文件夹路径"""
        dialog = FolderListDialog([])
        
        # 验证空路径
        result = dialog._validate_folder('')
        self.assertFalse(result)
        
        # 验证空白路径
        result = dialog._validate_folder('   ')
        self.assertFalse(result)

    @mock.patch('src.folder_list_dialog.QMessageBox.warning')
    def test_validate_folder_nonexistent(self, mock_msgbox):
        """测试验证不存在的文件夹"""
        dialog = FolderListDialog([])
        
        nonexistent_path = str(Path(__file__).parent / "definitely_not_exists")
        result = dialog._validate_folder(nonexistent_path)
        
        self.assertFalse(result)
        mock_msgbox.assert_called_once()

    @mock.patch('src.folder_list_dialog.QMessageBox.warning')
    def test_validate_folder_not_directory(self, mock_msgbox):
        """测试验证非文件夹路径（文件路径）"""
        dialog = FolderListDialog([])
        
        # 使用当前测试文件作为非文件夹路径
        file_path = str(Path(__file__))
        result = dialog._validate_folder(file_path)
        
        self.assertFalse(result)
        mock_msgbox.assert_called_once()

    def test_is_duplicate_folder_true(self):
        """测试检测重复文件夹"""
        dialog = FolderListDialog([self.test_folder1])
        
        # 使用相同路径
        result = dialog._is_duplicate_folder(self.test_folder1)
        self.assertTrue(result)
        
        # 使用规范化后相同的路径
        normalized_path = str(Path(self.test_folder1).resolve())
        result = dialog._is_duplicate_folder(normalized_path)
        self.assertTrue(result)

    def test_is_duplicate_folder_false(self):
        """测试检测非重复文件夹"""
        dialog = FolderListDialog([self.test_folder1])
        
        result = dialog._is_duplicate_folder(self.test_folder2)
        self.assertFalse(result)

    @mock.patch('src.folder_list_dialog.QMessageBox.question')
    def test_accept_with_empty_list(self, mock_msgbox):
        """测试确认空文件夹列表"""
        dialog = FolderListDialog([])
        
        # 模拟用户点击"否"
        mock_msgbox.return_value = QMessageBox.No
        
        dialog.accept()
        
        # 验证显示了确认对话框
        mock_msgbox.assert_called_once()

    @mock.patch('src.folder_list_dialog.QMessageBox.question')
    def test_accept_with_empty_list_confirmed(self, mock_msgbox):
        """测试确认空文件夹列表并同意"""
        dialog = FolderListDialog([])
        
        # 模拟用户点击"是"
        mock_msgbox.return_value = QMessageBox.Yes
        
        # 使用mock验证accept方法被调用
        with mock.patch.object(dialog, 'done') as mock_done:
            dialog.accept()
            mock_done.assert_called_once()

    def test_accept_with_folders(self):
        """测试确认有文件夹的列表"""
        dialog = FolderListDialog(self.initial_folders.copy())
        
        # 使用mock验证accept方法被调用
        with mock.patch.object(dialog, 'done') as mock_done:
            dialog.accept()
            mock_done.assert_called_once()

    def test_reject(self):
        """测试取消操作"""
        dialog = FolderListDialog(self.initial_folders.copy())
        
        # 使用mock验证reject方法被调用
        with mock.patch.object(dialog, 'done') as mock_done:
            dialog.reject()
            mock_done.assert_called_once()

    def test_folders_are_copied(self):
        """测试文件夹列表是副本而非引用"""
        original_folders = [self.test_folder1]
        dialog = FolderListDialog(original_folders)
        
        # 修改对话框中的文件夹列表
        dialog.folders.append(self.test_folder2)
        
        # 验证原始列表未被修改
        self.assertEqual(len(original_folders), 1)
        self.assertNotIn(self.test_folder2, original_folders)

    @mock.patch('src.folder_list_dialog.QFileDialog.getExistingDirectory')
    @mock.patch('src.folder_list_dialog.QMessageBox.critical')
    def test_add_folder_exception_handling(self, mock_critical, mock_file_dialog):
        """测试添加文件夹时的异常处理"""
        dialog = FolderListDialog([])
        
        # 模拟文件对话框抛出异常
        mock_file_dialog.side_effect = Exception("Test exception")
        
        dialog.add_folder()
        
        # 验证显示了错误消息
        mock_critical.assert_called_once()

    @mock.patch('src.folder_list_dialog.QMessageBox.critical')
    def test_remove_folder_exception_handling(self, mock_critical):
        """测试删除文件夹时的异常处理"""
        dialog = FolderListDialog([self.test_folder1])
        
        # 选择项目
        dialog.list_widget.setCurrentRow(0)
        
        # 模拟remove操作抛出异常
        with mock.patch.object(dialog.folders, 'remove', side_effect=Exception("Test exception")):
            dialog.remove_folder()
            
            # 验证显示了错误消息
            mock_critical.assert_called_once()

    @mock.patch('src.folder_list_dialog.QMessageBox.critical')
    def test_accept_exception_handling(self, mock_critical):
        """测试确认操作时的异常处理"""
        dialog = FolderListDialog([self.test_folder1])
        
        # 模拟super().accept()抛出异常
        with mock.patch('PySide6.QtWidgets.QDialog.accept', side_effect=Exception("Test exception")):
            dialog.accept()
            
            # 验证显示了错误消息
            mock_critical.assert_called_once()

    def test_reject_exception_handling(self):
        """测试取消操作时的异常处理"""
        dialog = FolderListDialog([self.test_folder1])
        
        # 模拟super().reject()抛出异常，应该被捕获并继续执行
        with mock.patch('PySide6.QtWidgets.QDialog.reject', side_effect=Exception("Test exception")):
            # 不应该抛出异常
            try:
                dialog.reject()
                # 如果没有异常，测试通过
                self.assertTrue(True)
            except:
                # 如果有异常逃逸，测试失败
                self.fail("Exception should be handled in reject method")

    def test_dialog_style_applied(self):
        """测试对话框样式是否已应用"""
        dialog = FolderListDialog([])
        
        # 验证样式表已设置
        self.assertNotEqual(dialog.styleSheet(), '')
        self.assertIn('QDialog', dialog.styleSheet())
        self.assertIn('QListWidget', dialog.styleSheet())
        self.assertIn('QPushButton', dialog.styleSheet())


if __name__ == '__main__':
    unittest.main()
