# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2020-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
{
    'name': 'Beauty Spa Management Salon Latam Alconsoft-Sistech',
    'summary': """Salon LATAM - Beauty Parlour Management with Online Booking System Alconsoft""",
    'version': '14.0.0.2',
    'author': 'Alejandro Concepcion',
    'website': "http://www.alconsoft.net",
    'company': 'Alconsoft-Sistech',
    "category": "Industries",
    'depends': ['salon_management','sale_management'],
    'data': [
             'views/salon_alconsoft.xml',
             'security/ir.model.access.csv'
             ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
}
