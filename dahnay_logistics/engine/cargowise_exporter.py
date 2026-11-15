"""
DahNAY FreightFlow Engine: CargoWise One Universal XML Exporter
Translates verified Shipping Instructions and pre-filled invoices into
production-compliant CargoWise UniversalShipment XML.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from dahnay_logistics.engine.models import ShippingInstruction, CommercialInvoice, MasterBookingRecord


class CargoWiseUniversalExporter:
    """Generates CargoWise One compatible Universal XML payloads."""

    @staticmethod
    def generate_universal_xml(
        si: ShippingInstruction,
        inv: CommercialInvoice,
        job: MasterBookingRecord
    ) -> str:
        root = ET.Element("UniversalShipment", xmlns="http://www.cargowise.com/Schemas/Universal/2011/11")
        shipment = ET.SubElement(root, "Shipment")

        # Context Header
        ctx = ET.SubElement(shipment, "DataContext")
        ET.SubElement(ctx, "Company").text = "DAHNAY_LOGISTICS_CHENNAI"
        ET.SubElement(ctx, "EnterpriseID").text = "DAHNAY"
        ET.SubElement(ctx, "ServerID").text = "PROD_IN"

        # Order Header
        order = ET.SubElement(shipment, "Order")
        ET.SubElement(order, "OrderNumber").text = job.booking_reference
        ET.SubElement(order, "ClientReference").text = si.si_number
        ET.SubElement(order, "JobReference").text = job.job_id

        # Routing / Transport Leg
        leg = ET.SubElement(order, "TransportLeg")
        ET.SubElement(leg, "TransportMode").text = "SEA"
        ET.SubElement(leg, "VesselName").text = si.vessel_name
        ET.SubElement(leg, "VoyageNumber").text = si.voyage_number
        ET.SubElement(leg, "PortOfLoading").text = si.port_of_loading
        ET.SubElement(leg, "PortOfDischarge").text = si.port_of_discharge

        # Parties
        parties = ET.SubElement(order, "Parties")
        
        shipper_node = ET.SubElement(parties, "Party", Type="Shipper")
        ET.SubElement(shipper_node, "Name").text = si.shipper_name
        ET.SubElement(shipper_node, "Address").text = si.shipper_address

        consignee_node = ET.SubElement(parties, "Party", Type="Consignee")
        ET.SubElement(consignee_node, "Name").text = si.consignee_name
        ET.SubElement(consignee_node, "Address").text = si.consignee_address

        # Containers
        cntrs_node = ET.SubElement(order, "Containers")
        for c in si.containers:
            c_elem = ET.SubElement(cntrs_node, "Container")
            ET.SubElement(c_elem, "ContainerNumber").text = c.container_number
            ET.SubElement(c_elem, "SealNumber").text = c.seal_number
            ET.SubElement(c_elem, "Type").text = c.container_type
            ET.SubElement(c_elem, "GrossWeightKG").text = str(c.gross_weight_kg)
            ET.SubElement(c_elem, "VolumeCBM").text = str(c.cbm)
            ET.SubElement(c_elem, "Packages").text = str(c.packages_count)

        # Commercial Invoice Summary
        inv_node = ET.SubElement(order, "CommercialInvoice")
        ET.SubElement(inv_node, "InvoiceNumber").text = inv.invoice_number
        ET.SubElement(inv_node, "BillTo").text = inv.bill_to_party
        ET.SubElement(inv_node, "TotalUSD").text = str(inv.total_usd)
        ET.SubElement(inv_node, "TotalINR").text = str(inv.grand_total_inr)
        ET.SubElement(inv_node, "GSTAmountINR").text = str(inv.gst_amount_inr)

        raw_xml = ET.tostring(root, encoding="utf-8")
        parsed = minidom.parseString(raw_xml)
        return parsed.toprettyxml(indent="  ")
