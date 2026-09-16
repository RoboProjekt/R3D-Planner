import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, PointField
from rclpy.qos import QoSProfile, DurabilityPolicy
import open3d as o3d
import numpy as np
import os

class PCDPublisher(Node):
    def __init__(self):
        super().__init__('pcd_publisher')
        
        # Parameter für den Dateipfad
        self.declare_parameter('pcd_path', 'environment.pcd')
        self.declare_parameter('map_frame', 'map')
        
        # QoS: TRANSIENT_LOCAL
        qos_profile = QoSProfile(depth=1)
        qos_profile.durability = DurabilityPolicy.TRANSIENT_LOCAL

        self.pub = self.create_publisher(PointCloud2, '/map_pointcloud', qos_profile)
        
        # Laden und Publishen
        self.load_and_publish()

    def load_and_publish(self):
        pcd_path = self.get_parameter('pcd_path').get_parameter_value().string_value
        pcd_path = os.path.abspath(os.path.expanduser(pcd_path))
        
        self.get_logger().info(f"Lade PCD Datei: {pcd_path}")
        
        if not os.path.exists(pcd_path):
            self.get_logger().error("Datei nicht gefunden!")
            return

        try:
            # 1. Mit Open3D laden
            pcd = o3d.io.read_point_cloud(pcd_path)
            if pcd.is_empty():
                self.get_logger().error("Punktwolke ist leer.")
                return

            # 2. In NumPy konvertieren
            points = np.asarray(pcd.points)
            self.get_logger().info(f"PCD geladen mit {len(points)} Punkten.")

            # Farben laden (falls vorhanden)
            colors = []
            if pcd.has_colors():
                colors = np.asarray(pcd.colors) # Open3D speichert RGB als 0.0-1.0 float

            # 3. PointCloud2 Nachricht erstellen
            msg = self.create_pc2_msg(points, colors)
            
            # 4. Publishen
            self.pub.publish(msg)
            self.get_logger().info("PCD erfolgreich auf /map_pointcloud veröffentlicht. (Mit Farben!)")

        except Exception as e:
            self.get_logger().error(f"Fehler beim Laden/Publishen: {e}")

    def create_pc2_msg(self, points, colors):
        msg = PointCloud2()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.get_parameter('map_frame').value

        # Basis-Layout (X, Y, Z)
        fields = [
            PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
        ]
        
        if len(colors) > 0:
            # Wenn Farbe dabei ist, hängen wir das RGB-Feld an (Byte-Offset 12)
            fields.append(PointField(name='rgb', offset=12, datatype=PointField.UINT32, count=1))
            msg.point_step = 16 # 3*4 Bytes (XYZ) + 1*4 Bytes (RGB)
            
            # Farben von float [0..1] zu uint8 [0..255] konvertieren
            colors_uint8 = (colors * 255.0).astype(np.uint32)
            
            # RGB in einen einzigen 32-Bit Integer packen (Bitshift)
            rgb_packed = (colors_uint8[:, 0] << 16) | (colors_uint8[:, 1] << 8) | colors_uint8[:, 2]
            
            # Numpy Array mit gemischten Datentypen erstellen (float32 für XYZ, uint32 für RGB)
            buffer = np.zeros(len(points), dtype=[
                ('x', np.float32),
                ('y', np.float32),
                ('z', np.float32),
                ('rgb', np.uint32)
            ])
            buffer['x'] = points[:, 0]
            buffer['y'] = points[:, 1]
            buffer['z'] = points[:, 2]
            buffer['rgb'] = rgb_packed
            
            msg.data = buffer.tobytes()
        else:
            msg.point_step = 12
            msg.data = points.astype(np.float32).tobytes()

        msg.height = 1
        msg.width = len(points)
        msg.fields = fields
        msg.is_bigendian = False
        msg.row_step = msg.point_step * points.shape[0]
        msg.is_dense = True
        
        return msg

def main(args=None):
    rclpy.init(args=args)
    node = PCDPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt: 
        pass
    finally:
        node.destroy_node()
        # Prüfen ob ROS noch läuft, bevor wir es beenden (verhindert den Fehler)
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
