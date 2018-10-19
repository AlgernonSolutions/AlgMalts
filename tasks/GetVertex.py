from MaltegoTransform import *
import sys

maltego_transform = MaltegoTransform()
internal_id = sys.argv[1]

entity = maltego_transform.addEntity("algernon.Vertex", "hello " + domain)

entity.set_type("maltego.Domain")
entity.setValue("Complex." + domain)
entity.setWeight(200)

entity.setDisplayInformation("<h3>Heading</h3><p>content here about" + domain + "!</p>")
entity.addAdditionalFields("variable", "Display Value", True, domain)

maltego_transform.addUIMessage("completed!")
maltego_transform.returnOutput()
