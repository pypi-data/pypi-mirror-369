import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QPushButton, QFrame, QScrollArea,
                               QGridLayout, QProgressBar, QSizePolicy)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QTimer
from PySide6.QtGui import QFont, QPixmap, QPainter, QPen, QBrush, QColor, QLinearGradient
import random
import math

class ModernCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.NoFrame)
        self.setStyleSheet("""
            QFrame {
                background-color: #2a2a3a;
                border-radius: 12px;
                border: 1px solid #3a3a4a;
            }
        """)
        
class IconLabel(QLabel):
    def __init__(self, color="#4a9eff", parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedSize(8, 8)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(self.color)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 8, 8)

class ProgressBarCustom(QProgressBar):
    def __init__(self, color="#4a9eff", parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedHeight(4)
        self.setTextVisible(False)
        self.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: #3a3a4a;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 2px;
            }}
        """)

class NetWorthChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(200)
        self.data_points = [
            800000, 820000, 830000, 850000, 860000, 865000, 
            870000, 875000, 880000, 890000, 900000, 902859
        ]
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw grid lines
        painter.setPen(QPen(QColor("#3a3a4a"), 1))
        for i in range(5):
            y = (i * self.height()) // 4
            painter.drawLine(0, y, self.width(), y)
            
        # Draw chart line
        if len(self.data_points) < 2:
            return
            
        min_val = min(self.data_points)
        max_val = max(self.data_points)
        val_range = max_val - min_val if max_val != min_val else 1
        
        points = []
        for i, value in enumerate(self.data_points):
            x = (i * self.width()) // (len(self.data_points) - 1)
            y = self.height() - int(((value - min_val) / val_range) * self.height())
            points.append((x, y))
        
        # Draw the line
        painter.setPen(QPen(QColor("#00ff88"), 2))
        for i in range(len(points) - 1):
            painter.drawLine(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
        
        # Draw points
        painter.setBrush(QBrush(QColor("#00ff88")))
        painter.setPen(Qt.NoPen)
        for x, y in points:
            painter.drawEllipse(x-3, y-3, 6, 6)

class SidebarButton(QPushButton):
    def __init__(self, text, icon_color="#666", parent=None):
        super().__init__(text, parent)
        self.icon_color = icon_color
        self.setFixedHeight(40)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                text-align: left;
                padding: 8px 12px;
                color: #ccc;
                font-size: 14px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #3a3a4a;
            }
            QPushButton:pressed {
                background-color: #4a4a5a;
            }
        """)

class AssetItem(QWidget):
    def __init__(self, name, value, change, change_type="up", category="Cash", parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        
        # Icon
        icon = IconLabel(self._get_category_color(category))
        layout.addWidget(icon)
        
        # Name
        name_label = QLabel(name)
        name_label.setStyleSheet("color: #ccc; font-size: 14px; font-weight: 500;")
        layout.addWidget(name_label)
        
        layout.addStretch()
        
        # Change
        change_color = "#00ff88" if change_type == "up" else "#ff4444"
        change_label = QLabel(change)
        change_label.setStyleSheet(f"color: {change_color}; font-size: 12px;")
        layout.addWidget(change_label)
        
        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet("color: #fff; font-size: 14px; font-weight: 600;")
        layout.addWidget(value_label)
        
    def _get_category_color(self, category):
        colors = {
            "Cash": "#4a9eff",
            "Investments": "#8b5cf6",
            "Crypto": "#fbbf24",
            "Properties": "#10b981",
            "Vehicles": "#ef4444",
            "Other Assets": "#6b7280"
        }
        return colors.get(category, "#4a9eff")

class CashflowChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(200)
        self.categories = [
            ("Food & Dining", 1200, "#ff6b6b"),
            ("Housing", 2800, "#4ecdc4"),
            ("Transportation", 800, "#45b7d1"),
            ("Entertainment", 500, "#96ceb4"),
            ("Healthcare", 600, "#feca57"),
            ("Shopping", 400, "#ff9ff3"),
            ("Travel", 300, "#54a0ff"),
            ("Miscellaneous", 200, "#5f27cd")
        ]
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Income bar
        income_rect = QRect(50, 50, 30, 100)
        painter.setBrush(QBrush(QColor("#00ff88")))
        painter.setPen(Qt.NoPen)
        painter.drawRect(income_rect)
        
        # Expenses bars
        total_expenses = sum(amount for _, amount, _ in self.categories)
        y_pos = 50
        
        for name, amount, color in self.categories:
            height = int((amount / total_expenses) * 100)
            expense_rect = QRect(120, y_pos, 30, height)
            painter.setBrush(QBrush(QColor(color)))
            painter.drawRect(expense_rect)
            y_pos += height

class FinanceDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fire App - Personal Finance Dashboard")
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a2e;
                color: #fff;
            }
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Main content
        content = self.create_main_content()
        main_layout.addWidget(content)
        
    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #16213e;
                border-right: 1px solid #2a2a3a;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Logo/Title
        title = QLabel("Fire App")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #fff; margin-bottom: 30px;")
        layout.addWidget(title)
        
        # Navigation
        nav_items = [
            ("🏠 Home", True),
            ("📊 Transactions", False),
            ("📈 Reports", False)
        ]
        
        for text, is_active in nav_items:
            btn = SidebarButton(text)
            if is_active:
                btn.setStyleSheet(btn.styleSheet() + "background-color: #2a2a3a;")
            layout.addWidget(btn)
        
        layout.addSpacing(30)
        
        # Assets section
        assets_label = QLabel("Assets")
        assets_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #fff; margin-bottom: 10px;")
        layout.addWidget(assets_label)
        
        # Add asset button
        add_asset_btn = QPushButton("+ New asset")
        add_asset_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px dashed #555;
                color: #888;
                padding: 8px;
                border-radius: 4px;
                text-align: center;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2a2a3a;
                border-color: #777;
            }
        """)
        layout.addWidget(add_asset_btn)
        
        # Assets list
        assets_data = [
            ("Cash", "$172,693.00", "+2.1%", "up"),
            ("Chase Premier Checking", "$194,394.00", "+3.4%", "up"),
            ("Marcus High-Yield Savings", "$81,348.00", "-1.2%", "down"),
            ("Ally Online Checking", "$9,823.00", "+0.5%", "up"),
            ("Deutsche Bank EUR Account", "$29,824.00", "+1.8%", "up"),
        ]
        
        for name, value, change, change_type in assets_data:
            item = AssetItem(name, value, change, change_type, "Cash")
            layout.addWidget(item)
        
        layout.addSpacing(20)
        
        # Investments section
        investments_label = QLabel("Investments")
        investments_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #fff; margin-bottom: 10px;")
        layout.addWidget(investments_label)
        
        investments_data = [
            ("Charles Schwab Brokerage", "$253,484.58", "+8.2%", "up"),
            ("Fidelity HSA Investment", "$17,275.00", "+5.1%", "up"),
            ("Vanguard 401(k)", "$257,840.21", "+12.3%", "up"),
            ("Fidelity Roth IRA", "$39,459.30", "+7.8%", "up"),
            ("Vanguard UK ISA", "$34,850.25", "+4.2%", "up"),
        ]
        
        for name, value, change, change_type in investments_data:
            item = AssetItem(name, value, change, change_type, "Investments")
            layout.addWidget(item)
        
        layout.addStretch()
        
        return sidebar
    
    def create_main_content(self):
        content = QWidget()
        content.setStyleSheet("background-color: #1a1a2e;")
        
        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Main dashboard content
        dashboard_content = self.create_dashboard_content()
        layout.addWidget(dashboard_content)
        
        return content
    
    def create_header(self):
        header = QWidget()
        header.setFixedHeight(80)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 20)
        
        # Welcome message
        welcome_layout = QVBoxLayout()
        
        title = QLabel("Welcome back, Demo (admin)")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #fff;")
        welcome_layout.addWidget(title)
        
        subtitle = QLabel("Here's what's happening with your finances.")
        subtitle.setStyleSheet("font-size: 14px; color: #888; margin-top: 5px;")
        welcome_layout.addWidget(subtitle)
        
        layout.addLayout(welcome_layout)
        layout.addStretch()
        
        # New button
        new_btn = QPushButton("+ New")
        new_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #3a8eef;
            }
            QPushButton:pressed {
                background-color: #2a7edf;
            }
        """)
        layout.addWidget(new_btn)
        
        return header
    
    def create_dashboard_content(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2a2a3a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #4a4a5a;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #5a5a6a;
            }
        """)
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # Net Worth section
        net_worth_card = self.create_net_worth_card()
        layout.addWidget(net_worth_card)
        
        layout.addSpacing(20)
        
        # Assets and Liabilities row
        assets_liabilities_row = QHBoxLayout()
        
        # Assets card
        assets_card = self.create_assets_card()
        assets_liabilities_row.addWidget(assets_card, 1)
        
        assets_liabilities_row.addSpacing(20)
        
        # Liabilities card
        liabilities_card = self.create_liabilities_card()
        assets_liabilities_row.addWidget(liabilities_card, 1)
        
        layout.addLayout(assets_liabilities_row)
        
        layout.addSpacing(20)
        
        # Cashflow card
        cashflow_card = self.create_cashflow_card()
        layout.addWidget(cashflow_card)
        
        layout.addStretch()
        
        scroll.setWidget(content_widget)
        return scroll
    
    def create_net_worth_card(self):
        card = ModernCard()
        card.setFixedHeight(320)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(25, 20, 25, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        net_worth_label = QLabel("Net Worth")
        net_worth_label.setStyleSheet("font-size: 16px; color: #888; font-weight: 500;")
        header_layout.addWidget(net_worth_label)
        
        header_layout.addStretch()
        
        period_label = QLabel("30D")
        period_label.setStyleSheet("font-size: 14px; color: #888;")
        header_layout.addWidget(period_label)
        
        layout.addLayout(header_layout)
        
        # Net worth value
        value_layout = QHBoxLayout()
        
        net_worth_value = QLabel("$902,859.34")
        net_worth_value.setStyleSheet("font-size: 32px; font-weight: bold; color: #fff; margin: 10px 0;")
        value_layout.addWidget(net_worth_value)
        
        value_layout.addStretch()
        
        layout.addLayout(value_layout)
        
        # Change indicator
        change_layout = QHBoxLayout()
        
        change_label = QLabel("$308,662.58")
        change_label.setStyleSheet("color: #00ff88; font-size: 14px; font-weight: 500;")
        change_layout.addWidget(change_label)
        
        change_percent = QLabel("▲ 70.1% vs last month")
        change_percent.setStyleSheet("color: #00ff88; font-size: 12px; margin-left: 10px;")
        change_layout.addWidget(change_percent)
        
        change_layout.addStretch()
        
        layout.addLayout(change_layout)
        
        layout.addSpacing(20)
        
        # Chart
        chart = NetWorthChart()
        layout.addWidget(chart)
        
        return card
    
    def create_assets_card(self):
        card = ModernCard()
        card.setMinimumHeight(400)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(25, 20, 25, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        assets_label = QLabel("Assets")
        assets_label.setStyleSheet("font-size: 16px; color: #888; font-weight: 500;")
        header_layout.addWidget(assets_label)
        
        total_label = QLabel("$1,153,702")
        total_label.setStyleSheet("font-size: 16px; color: #fff; font-weight: 600;")
        header_layout.addWidget(total_label)
        
        layout.addLayout(header_layout)
        
        layout.addSpacing(10)
        
        # Progress bars for asset allocation
        asset_data = [
            ("Cash", 15, "#4a9eff", "$172,693.00", "14.97%"),
            ("Investments", 52, "#8b5cf6", "$603,009.34", "52.27%"),
            ("Crypto", 1, "#fbbf24", "$3,500.00", "0.30%"),
            ("Properties", 30, "#10b981", "$350,000.00", "30.34%"),
            ("Vehicles", 2, "#ef4444", "$22,500.00", "1.95%"),
            ("Other Assets", 0, "#6b7280", "$2,000.00", "0.17%")
        ]
        
        # Combined progress bar
        combined_progress = QWidget()
        combined_progress.setFixedHeight(8)
        combined_layout = QHBoxLayout(combined_progress)
        combined_layout.setContentsMargins(0, 0, 0, 0)
        combined_layout.setSpacing(1)
        
        for name, percentage, color, value, weight in asset_data:
            if percentage > 0:
                bar_segment = QWidget()
                bar_segment.setStyleSheet(f"background-color: {color}; border-radius: 4px;")
                combined_layout.addWidget(bar_segment, percentage)
        
        layout.addWidget(combined_progress)
        
        layout.addSpacing(20)
        
        # Asset breakdown
        for name, percentage, color, value, weight in asset_data:
            asset_row = QWidget()
            asset_layout = QHBoxLayout(asset_row)
            asset_layout.setContentsMargins(0, 8, 0, 8)
            
            # Color indicator
            color_dot = IconLabel(color)
            asset_layout.addWidget(color_dot)
            
            # Name
            name_label = QLabel(name)
            name_label.setStyleSheet("color: #ccc; font-size: 14px;")
            asset_layout.addWidget(name_label)
            
            asset_layout.addStretch()
            
            # Weight
            weight_label = QLabel(weight)
            weight_label.setStyleSheet("color: #888; font-size: 12px;")
            asset_layout.addWidget(weight_label)
            
            # Value
            value_label = QLabel(value)
            value_label.setStyleSheet("color: #fff; font-size: 14px; font-weight: 500;")
            asset_layout.addWidget(value_label)
            
            layout.addWidget(asset_row)
        
        return card
    
    def create_liabilities_card(self):
        card = ModernCard()
        card.setMinimumHeight(400)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(25, 20, 25, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        liabilities_label = QLabel("Liabilities")
        liabilities_label.setStyleSheet("font-size: 16px; color: #888; font-weight: 500;")
        header_layout.addWidget(liabilities_label)
        
        total_label = QLabel("$250,843")
        total_label.setStyleSheet("font-size: 16px; color: #fff; font-weight: 600;")
        header_layout.addWidget(total_label)
        
        layout.addLayout(header_layout)
        
        layout.addSpacing(10)
        
        # Progress bars for liabilities
        liability_data = [
            ("Credit Cards", 2, "#ff4444", "$5,093.00", "2.03%"),
            ("Loans", 98, "#ff6b6b", "$244,950.00", "97.65%"),
            ("Other Liabilities", 0, "#6b7280", "$800.00", "0.32%")
        ]
        
        # Combined progress bar
        combined_progress = QWidget()
        combined_progress.setFixedHeight(8)
        combined_layout = QHBoxLayout(combined_progress)
        combined_layout.setContentsMargins(0, 0, 0, 0)
        combined_layout.setSpacing(1)
        
        for name, percentage, color, value, weight in liability_data:
            if percentage > 0:
                bar_segment = QWidget()
                bar_segment.setStyleSheet(f"background-color: {color}; border-radius: 4px;")
                combined_layout.addWidget(bar_segment, percentage)
        
        layout.addWidget(combined_progress)
        
        layout.addSpacing(20)
        
        # Liability breakdown
        for name, percentage, color, value, weight in liability_data:
            liability_row = QWidget()
            liability_layout = QHBoxLayout(liability_row)
            liability_layout.setContentsMargins(0, 8, 0, 8)
            
            # Color indicator
            color_dot = IconLabel(color)
            liability_layout.addWidget(color_dot)
            
            # Name
            name_label = QLabel(name)
            name_label.setStyleSheet("color: #ccc; font-size: 14px;")
            liability_layout.addWidget(name_label)
            
            liability_layout.addStretch()
            
            # Weight
            weight_label = QLabel(weight)
            weight_label.setStyleSheet("color: #888; font-size: 12px;")
            liability_layout.addWidget(weight_label)
            
            # Value
            value_label = QLabel(value)
            value_label.setStyleSheet("color: #fff; font-size: 14px; font-weight: 500;")
            liability_layout.addWidget(value_label)
            
            layout.addWidget(liability_row)
        
        layout.addStretch()
        
        return card
    
    def create_cashflow_card(self):
        card = ModernCard()
        card.setFixedHeight(350)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(25, 20, 25, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        cashflow_label = QLabel("Cashflow")
        cashflow_label.setStyleSheet("font-size: 16px; color: #888; font-weight: 500;")
        header_layout.addWidget(cashflow_label)
        
        header_layout.addStretch()
        
        period_label = QLabel("30D")
        period_label.setStyleSheet("font-size: 14px; color: #888;")
        header_layout.addWidget(period_label)
        
        layout.addLayout(header_layout)
        
        # Chart and legend layout
        content_layout = QHBoxLayout()
        
        # Chart
        chart = CashflowChart()
        content_layout.addWidget(chart, 1)
        
        # Legend
        legend_widget = QWidget()
        legend_layout = QVBoxLayout(legend_widget)
        legend_layout.setContentsMargins(20, 0, 0, 0)
        
        categories = [
            ("Food & Dining", "$1,200", "#ff6b6b"),
            ("Housing", "$2,800", "#4ecdc4"),
            ("Transportation", "$800", "#45b7d1"),
            ("Entertainment", "$500", "#96ceb4"),
            ("Healthcare", "$600", "#feca57"),
            ("Shopping", "$400", "#ff9ff3"),
            ("Travel", "$300", "#54a0ff"),
            ("Miscellaneous", "$200", "#5f27cd"),
            ("Uncategorized", "$8,312", "#6b7280")
        ]
        
        for name, amount, color in categories:
            legend_row = QWidget()
            legend_row_layout = QHBoxLayout(legend_row)
            legend_row_layout.setContentsMargins(0, 2, 0, 2)
            
            # Color dot
            color_dot = IconLabel(color)
            legend_row_layout.addWidget(color_dot)
            
            # Category name
            name_label = QLabel(name)
            name_label.setStyleSheet("color: #ccc; font-size: 12px;")
            legend_row_layout.addWidget(name_label)
            
            legend_row_layout.addStretch()
            
            # Amount
            amount_label = QLabel(amount)
            amount_label.setStyleSheet("color: #fff; font-size: 12px; font-weight: 500;")
            legend_row_layout.addWidget(amount_label)
            
            legend_layout.addWidget(legend_row)
        
        legend_layout.addStretch()
        
        content_layout.addWidget(legend_widget, 1)
        
        layout.addLayout(content_layout)
        
        return card

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = FinanceDashboard()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()