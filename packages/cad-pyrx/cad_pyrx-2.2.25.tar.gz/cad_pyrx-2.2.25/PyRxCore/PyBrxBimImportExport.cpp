#include "stdafx.h"
#include "PyBrxBimImportExport.h"

#ifdef BRXAPP
#include "PyDbDatabase.h"
#include "PyDbObjectId.h"
#include "PyDbEntity.h"
#include "PyDb3dSolid.h"
#include "PyApDocument.h"
#include "PyBrxIfc.h"

using namespace boost::python;

void makePyBrxIfcImportOptionsWrapper()
{
    PyDocString DS("IfcImportOptions");
    class_<PyBrxIfcImportOptions>("IfcImportOptions")
        .def("importBimData", &PyBrxIfcImportOptions::importBimData, DS.ARGS())
        .def("setImportBimData", &PyBrxIfcImportOptions::setImportBimData, DS.ARGS({ "val: bool" }))
        .def("importIfcSpace", &PyBrxIfcImportOptions::importIfcSpace, DS.ARGS())
        .def("setImportIfcSpace", &PyBrxIfcImportOptions::setImportIfcSpace, DS.ARGS({ "val: bool" }))
        .def("importParametricComponents", &PyBrxIfcImportOptions::importParametricComponents, DS.ARGS())
        .def("setImportParametricComponents", &PyBrxIfcImportOptions::setImportParametricComponents, DS.ARGS({ "val: bool" }))
        .def("importIfcProjectStructureAsXrefs", &PyBrxIfcImportOptions::importIfcProjectStructureAsXrefs, DS.ARGS())
        .def("setImportIfcProjectStructureAsXrefs", &PyBrxIfcImportOptions::setImportIfcProjectStructureAsXrefs, DS.ARGS({ "val: bool" }))
        .def("importBrepGeometryAsMeshes", &PyBrxIfcImportOptions::importBrepGeometryAsMeshes, DS.ARGS())
        .def("setImportBrepGeometryAsMeshes", &PyBrxIfcImportOptions::setImportBrepGeometryAsMeshes, DS.ARGS({ "val: bool" }))
        .def("importModelOrigin", &PyBrxIfcImportOptions::importModelOrigin, DS.ARGS())
        .def("setImportModelOrigin", &PyBrxIfcImportOptions::setImportModelOrigin, DS.ARGS({ "val: PyBrxBim.IfcImportModelOrigin" }))
        .def("importIfcFile", &PyBrxIfcImportOptions::importIfcFile1)
        .def("importIfcFile", &PyBrxIfcImportOptions::importIfcFile2, DS.SARGS({ "db: PyDb.Database", "filename: str", "options: PyBrxBim.IfcImportOptions = ..." })).staticmethod("importIfcFile")
        .def("className", &PyBrxIfcImportOptions::className, DS.SARGS()).staticmethod("className")
        ;
}

PyBrxIfcImportOptions::PyBrxIfcImportOptions()
    :PyBrxIfcImportOptions(new BimApi::BrxIfcImportOptions(), true)
{
}

PyBrxIfcImportOptions::PyBrxIfcImportOptions(const BimApi::BrxIfcImportOptions* pObject)
    :PyBrxIfcImportOptions(const_cast<BimApi::BrxIfcImportOptions*>(pObject), false)
{
}

PyBrxIfcImportOptions::PyBrxIfcImportOptions(BimApi::BrxIfcImportOptions* pObject, bool autoDelete)
    : m_pyImp(pObject, PySharedObjectDeleter<BimApi::BrxIfcImportOptions>(autoDelete))
{
}

bool PyBrxIfcImportOptions::importBimData() const
{
    return impObj()->importBimData();
}

void PyBrxIfcImportOptions::setImportBimData(bool bOn) const
{
    impObj()->setImportBimData(bOn);
}

bool PyBrxIfcImportOptions::importIfcSpace() const
{
    return impObj()->importIfcSpace();
}

void PyBrxIfcImportOptions::setImportIfcSpace(bool bOn) const
{
    impObj()->setImportIfcSpace(bOn);
}

bool PyBrxIfcImportOptions::importParametricComponents() const
{
    return impObj()->importParametricComponents();
}

void PyBrxIfcImportOptions::setImportParametricComponents(bool bOn) const
{
    impObj()->setImportParametricComponents(bOn);
}

bool PyBrxIfcImportOptions::importIfcProjectStructureAsXrefs() const
{
    return impObj()->importIfcProjectStructureAsXrefs();
}

void PyBrxIfcImportOptions::setImportIfcProjectStructureAsXrefs(bool bOn) const
{
    impObj()->setImportIfcProjectStructureAsXrefs(bOn);
}

bool PyBrxIfcImportOptions::importBrepGeometryAsMeshes() const
{
    return impObj()->importBrepGeometryAsMeshes();
}

void PyBrxIfcImportOptions::setImportBrepGeometryAsMeshes(bool bOn) const
{
    impObj()->setImportBrepGeometryAsMeshes(bOn);
}

BimApi::EIfcImportModelOrigin PyBrxIfcImportOptions::importModelOrigin() const
{
    return impObj()->importModelOrigin();
}

void PyBrxIfcImportOptions::setImportModelOrigin(BimApi::EIfcImportModelOrigin mode) const
{
    impObj()->setImportModelOrigin(mode);
}

void PyBrxIfcImportOptions::importIfcFile1(PyDbDatabase& pDb, const std::string szFilename)
{
    PyThrowBadBim(BimApi::importIfcFile(pDb.impObj(), utf8_to_wstr(szFilename).c_str()));
}

void PyBrxIfcImportOptions::importIfcFile2(PyDbDatabase& pDb, const std::string szFilename, const PyBrxIfcImportOptions& pOptions)
{
    PyThrowBadBim(BimApi::importIfcFile(pDb.impObj(), utf8_to_wstr(szFilename).c_str(), pOptions.impObj()));
}

std::string PyBrxIfcImportOptions::className()
{
    return "BrxIfcImportOptions";
}

BimApi::BrxIfcImportOptions* PyBrxIfcImportOptions::impObj(const std::source_location& src /*= std::source_location::current()*/) const
{
    if (m_pyImp == nullptr) [[unlikely]] {
        throw PyNullObject(src);
    }
    return static_cast<BimApi::BrxIfcImportOptions*>(m_pyImp.get());
}

//---------------------------------------------------------------------------------------- -
//PyBrxBimIfcImportInfo
void makePyBrxBimIfcImportInfoWrapper()
{
    PyDocString DS("IfcImportInfo");
    class_<PyBrxBimIfcImportInfo>("IfcImportInfo")
        .def("className", &PyBrxBimIfcImportInfo::fileName, DS.ARGS())
        .def("timeStamp", &PyBrxBimIfcImportInfo::timeStamp, DS.ARGS())
        .def("author", &PyBrxBimIfcImportInfo::author, DS.ARGS())
        .def("organization", &PyBrxBimIfcImportInfo::organization, DS.ARGS())
        .def("preprocessorVersion", &PyBrxBimIfcImportInfo::preprocessorVersion, DS.ARGS())
        .def("originatingSystem", &PyBrxBimIfcImportInfo::originatingSystem, DS.ARGS())
        .def("authorization", &PyBrxBimIfcImportInfo::authorization, DS.ARGS())
        .def("importBimData", &PyBrxBimIfcImportInfo::importBimData, DS.ARGS())
        .def("importIfcSpace", &PyBrxBimIfcImportInfo::importIfcSpace, DS.ARGS())
        .def("importParametricComponents", &PyBrxBimIfcImportInfo::importParametricComponents, DS.ARGS())
        .def("importIfcProjectStructureAsXrefs", &PyBrxBimIfcImportInfo::importIfcProjectStructureAsXrefs, DS.ARGS())
        .def("importBrepGeometryAsMeshes", &PyBrxBimIfcImportInfo::importBrepGeometryAsMeshes, DS.ARGS())
        .def("className", &PyBrxBimIfcImportInfo::className, DS.SARGS()).staticmethod("className")
        ;
}

PyBrxBimIfcImportInfo::PyBrxBimIfcImportInfo()
    :PyBrxBimIfcImportInfo(new BimIfcImportInfo(), true)
{
}

PyBrxBimIfcImportInfo::PyBrxBimIfcImportInfo(BrxIfcTranslatorOptions* opts, Ice::IfcApi::Header* header)
    :PyBrxBimIfcImportInfo(new BimIfcImportInfo(opts, header), true)
{
}

PyBrxBimIfcImportInfo::PyBrxBimIfcImportInfo(const BimIfcImportInfo* pObject)
    :PyBrxBimIfcImportInfo(const_cast<BimIfcImportInfo*>(pObject), false)
{
}

PyBrxBimIfcImportInfo::PyBrxBimIfcImportInfo(BimIfcImportInfo* pObject, bool autoDelete)
    : m_pyImp(pObject, PySharedObjectDeleter<BimIfcImportInfo>(autoDelete))
{
}

std::string PyBrxBimIfcImportInfo::fileName() const
{
    return wstr_to_utf8(impObj()->fileName());
}

std::string PyBrxBimIfcImportInfo::timeStamp() const
{
    return wstr_to_utf8(impObj()->timeStamp());
}

std::string PyBrxBimIfcImportInfo::author() const
{
    return wstr_to_utf8(impObj()->author());
}

std::string PyBrxBimIfcImportInfo::organization() const
{
    return wstr_to_utf8(impObj()->organization());
}

std::string PyBrxBimIfcImportInfo::preprocessorVersion() const
{
    return wstr_to_utf8(impObj()->preprocessorVersion());
}

std::string PyBrxBimIfcImportInfo::originatingSystem() const
{
    return wstr_to_utf8(impObj()->originatingSystem());
}

std::string PyBrxBimIfcImportInfo::authorization() const
{
    return wstr_to_utf8(impObj()->authorization());
}

bool PyBrxBimIfcImportInfo::importBimData() const
{
    return impObj()->importBimData();
}

bool PyBrxBimIfcImportInfo::importIfcSpace() const
{
    return impObj()->importIfcSpace();
}

bool PyBrxBimIfcImportInfo::importParametricComponents() const
{
    return impObj()->importParametricComponents();
}

bool PyBrxBimIfcImportInfo::importIfcProjectStructureAsXrefs() const
{
    return impObj()->importIfcProjectStructureAsXrefs();
}

bool PyBrxBimIfcImportInfo::importBrepGeometryAsMeshes() const
{
    return impObj()->importBrepGeometryAsMeshes();
}

std::string PyBrxBimIfcImportInfo::className()
{
    return "BimIfcImportInfo";
}

BimIfcImportInfo* PyBrxBimIfcImportInfo::impObj(const std::source_location& src /*= std::source_location::current()*/) const
{
    if (m_pyImp == nullptr) [[unlikely]] {
        throw PyNullObject(src);
    }
    return static_cast<BimIfcImportInfo*>(m_pyImp.get());
}

//---------------------------------------------------------------------------------------- -
//BrxBimIfcImportContext
void makePyBrxBimIfcImportContextWrapper()
{
    PyDocString DS("IfcImportContext");
    class_<PyBrxBimIfcImportContext>("IfcImportContext", boost::python::no_init)
        .def("IfcModel", &PyBrxBimIfcImportContext::ifcModel, DS.ARGS())
        .def("database", &PyBrxBimIfcImportContext::database, DS.ARGS())
        .def("createDefaultRepresentation", &PyBrxBimIfcImportContext::createDefaultRepresentation, DS.ARGS({ "entity: PyBrxBim.IfcEntity","isParent: bool" , "parent: PyBrxBim.IfcEntity" }))
        .def("createRepresentationFromItem", &PyBrxBimIfcImportContext::createRepresentationFromItem, DS.ARGS({ "entity: PyBrxBim.IfcEntity" }))
        .def("createPoint", &PyBrxBimIfcImportContext::createPoint, DS.ARGS({ "entity: PyBrxBim.IfcEntity" }))
        .def("getLocalPlacement", &PyBrxBimIfcImportContext::getLocalPlacement, DS.ARGS({ "entity: PyBrxBim.IfcEntity" }))
        .def("createSweptArea", &PyBrxBimIfcImportContext::createSweptArea, DS.ARGS({ "entity: PyBrxBim.IfcEntity" }))
        .def("getEntity", &PyBrxBimIfcImportContext::getEntity, DS.ARGS({ "entity: PyBrxBim.IfcEntity" }))
        .def("getEntityId", &PyBrxBimIfcImportContext::getEntityId, DS.ARGS({ "entity: PyBrxBim.IfcEntity" }))
        .def("angleConversionFactor", &PyBrxBimIfcImportContext::angleConversionFactor, DS.ARGS())
        .def("areaConversionFactor", &PyBrxBimIfcImportContext::areaConversionFactor, DS.ARGS())
        .def("lengthConversionFactor", &PyBrxBimIfcImportContext::lengthConversionFactor, DS.ARGS())
        .def("volumeConversionFactor", &PyBrxBimIfcImportContext::volumeConversionFactor, DS.ARGS())
        .def("precision", &PyBrxBimIfcImportContext::precision, DS.ARGS())
        .def("className", &PyBrxBimIfcImportContext::className, DS.SARGS()).staticmethod("className")
        ;
}

PyBrxBimIfcImportContext::PyBrxBimIfcImportContext(const IfcImportContext* pObject)
    :PyBrxBimIfcImportContext(const_cast<IfcImportContext*>(pObject), false)
{
}

PyBrxBimIfcImportContext::PyBrxBimIfcImportContext(IfcImportContext* pObject, bool autoDelete)
    : m_pyImp(pObject, PySharedObjectDeleter<IfcImportContext>(autoDelete))
{
}

PyIfcModel PyBrxBimIfcImportContext::ifcModel() const
{
    return PyIfcModel(impObj()->ifcModel(), false);
}

PyDbDatabase PyBrxBimIfcImportContext::database() const
{
    return PyDbDatabase(impObj()->database());
}

PyDbEntity PyBrxBimIfcImportContext::createDefaultRepresentation(const PyIfcEntity& entity, bool isParent, const PyIfcEntity& parent) const
{
    return PyDbEntity(impObj()->createDefaultRepresentation(*entity.impObj(), isParent, *parent.impObj()), true);
}

PyDbEntity PyBrxBimIfcImportContext::createRepresentationFromItem(const PyIfcEntity& entity) const
{
    return PyDbEntity(impObj()->createRepresentationFromItem(*entity.impObj()), true);
}

AcGePoint3d PyBrxBimIfcImportContext::createPoint(const PyIfcEntity& point) const
{
    return impObj()->createPoint(*point.impObj());
}

AcGeMatrix3d PyBrxBimIfcImportContext::getLocalPlacement(const PyIfcEntity& point) const
{
    return impObj()->getLocalPlacement(*point.impObj());
}

boost::python::list PyBrxBimIfcImportContext::createSweptArea(const PyIfcEntity& sweptArea) const
{
    PyAutoLockGIL lock;
    boost::python::list pylist;
    for (auto ptr : impObj()->createSweptArea(*sweptArea.impObj()))
        pylist.append(PyDbEntity(ptr, true));
    return pylist;
}

PyDbEntity PyBrxBimIfcImportContext::getEntity(const PyIfcEntity& IfcEntity)
{
    AcDbEntity* pEnt = nullptr;
    if (bool flag = impObj()->getEntity(pEnt, *IfcEntity.impObj()); flag == false)
        PyThrowBadBim(BimApi::eInvalidInput);
    return PyDbEntity(pEnt, true);
}

PyDbObjectId PyBrxBimIfcImportContext::getEntityId(const PyIfcEntity& IfcEntity)
{
    PyDbObjectId id;
    if (bool flag = impObj()->getEntity(id.m_id, *IfcEntity.impObj()); flag == false)
        PyThrowBadBim(BimApi::eInvalidInput);
    return id;
}

double PyBrxBimIfcImportContext::angleConversionFactor() const
{
    return impObj()->angleConversionFactor();
}

double PyBrxBimIfcImportContext::areaConversionFactor() const
{
    return impObj()->areaConversionFactor();
}

double PyBrxBimIfcImportContext::lengthConversionFactor() const
{
    return impObj()->lengthConversionFactor();
}

double PyBrxBimIfcImportContext::volumeConversionFactor() const
{
    return impObj()->volumeConversionFactor();
}

double PyBrxBimIfcImportContext::precision() const
{
    return impObj()->precision();
}

std::string PyBrxBimIfcImportContext::className()
{
    return "BimIfcImportContext";
}

IfcImportContext* PyBrxBimIfcImportContext::impObj(const std::source_location& src /*= std::source_location::current()*/) const
{
    if (m_pyImp == nullptr) [[unlikely]] {
        throw PyNullObject(src);
    }
    return static_cast<IfcImportContext*>(m_pyImp.get());
}


//---------------------------------------------------------------------------------------- -
//PyBimIfcImportReactorImpl
PyBimIfcImportReactorImpl::PyBimIfcImportReactorImpl(PyBimIfcImportReactor* ptr, const AcString& displayName, const AcString& guid)
    : m_pyBackPtr(ptr), m_displayName(displayName), m_guid(guid)
{
    m_instance = this;
}

void PyBimIfcImportReactorImpl::onStart(BimIfcImportReactorInstance::Context& context, const Ice::IfcApi::Entity& project, const BimIfcImportInfo& info)
{
    if (impObj()->reg_onStart)
    {
        PyBrxBimIfcImportContext ctx(std::addressof(context));
        PyIfcEntity ent(std::addressof(project));
        PyBrxBimIfcImportInfo _info(std::addressof(info));
        impObj()->onStart(ctx, ent, _info);
    }
}

bool PyBimIfcImportReactorImpl::onIfcProduct(BimIfcImportReactorInstance::Context& context, const Ice::IfcApi::Entity& entity, bool isParent, const Ice::IfcApi::Entity& parentEntity)
{
    if (impObj()->reg_onIfcProduct)
    {
        PyBrxBimIfcImportContext ctx(std::addressof(context));
        PyIfcEntity ent(std::addressof(entity));
        PyIfcEntity parent(std::addressof(parentEntity));
        return impObj()->onIfcProduct(ctx, ent, isParent, parent);
    }
    return false;
}

void PyBimIfcImportReactorImpl::beforeCompletion(BimIfcImportReactorInstance::Context& context, bool success)
{
    if (impObj()->reg_beforeCompletion)
    {
        PyBrxBimIfcImportContext ctx(std::addressof(context));
        impObj()->beforeCompletion(ctx, success);
    }
}

void PyBimIfcImportReactorImpl::onIfcProductImported(
    const Ice::IfcApi::Entity& sourceEntity,
    bool isParent,
    const Ice::IfcApi::Entity& sourceParentEntity,
    AcDbEntityPtrArray& createdAcEntites,
    const AcGeMatrix3d* constructedAcEntityTransformation)
{
    if (impObj()->reg_onIfcProductImported)
    {
        PyIfcEntity _sourceEntity(std::addressof(sourceEntity));
        PyIfcEntity _sourceParentEntity(std::addressof(sourceParentEntity));

        boost::python::list pycreatedAcEntites;
        for (AcDbEntity* pEnt : createdAcEntites)
            pycreatedAcEntites.append(PyDbEntity(pEnt, true));

        if (constructedAcEntityTransformation != nullptr)
            impObj()->onIfcProductImported(_sourceEntity, isParent, _sourceParentEntity, pycreatedAcEntites, *constructedAcEntityTransformation);
        else
            impObj()->onIfcProductImported(_sourceEntity, isParent, _sourceParentEntity, pycreatedAcEntites, AcGeMatrix3d::kIdentity);
    }
}

BimIfcImportReactorInstance* PyBimIfcImportReactorImpl::getIfcReactorInstance(Ice::EIfcSchemaId schema)
{
    return m_instance;
}

const ACHAR* PyBimIfcImportReactorImpl::GUID() const
{
    return m_guid;
}

const ACHAR* PyBimIfcImportReactorImpl::displayName() const
{
    return m_displayName;
}

PyBimIfcImportReactor* PyBimIfcImportReactorImpl::impObj(const std::source_location& src /*= std::source_location::current()*/) const
{
    if (m_pyBackPtr == nullptr) [[unlikely]] {
        throw PyNullObject(src);
    }
    return m_pyBackPtr;
}

//---------------------------------------------------------------------------------------- -
//BimIfcImportReactor
void makePyBimIfcImportReactorWrapper()
{
    PyDocString DS("IfcImportReactor");
    class_<PyBimIfcImportReactor>("IfcImportReactor", boost::python::no_init)
        .def(init<const std::string&, const std::string&>(DS.ARGS({ "displayName: str","guid: str" })))
        .def("onStart", &PyBimIfcImportReactor::onStart, DS.ARGS({ "context: PyBrxBim.IfcImportContext", "project:  PyBrxBim.IfcEntity", "info: PyBrxBim.IfcImportInfo" }))
        .def("onIfcProduct", &PyBimIfcImportReactor::onIfcProduct, DS.ARGS({ "context: PyBrxBim.IfcImportContext", "entity:  PyBrxBim.IfcEntity", "isParent: bool","parentEntity:  PyBrxBim.IfcEntity" }))
        .def("beforeCompletion", &PyBimIfcImportReactor::beforeCompletion, DS.ARGS({ "context: PyBrxBim.IfcImportContext", "success: bool" }))
        .def("onIfcProductImported", &PyBimIfcImportReactor::onIfcProductImported, DS.ARGS({ "desc: PyBrxBim.IfcEntityDesc", "schema: PyBrxBim.EIfcSchemaId" }))
        .def("attachReactor", &PyBimIfcImportReactor::attachReactor, DS.ARGS())
        .def("detachReactor", &PyBimIfcImportReactor::detachReactor, DS.ARGS())
        .def("className", &PyBimIfcImportReactor::className, DS.SARGS()).staticmethod("className")
        ;
}

PyBimIfcImportReactor::PyBimIfcImportReactor(const std::string& displayName, const std::string& GUID)
    : PyBimIfcImportReactor(new PyBimIfcImportReactorImpl(this, utf8_to_wstr(GUID).c_str(), utf8_to_wstr(displayName).c_str()), true)
{
}

PyBimIfcImportReactor::PyBimIfcImportReactor(const PyBimIfcImportReactorImpl* pObject)
    :PyBimIfcImportReactor(const_cast<PyBimIfcImportReactorImpl*>(pObject), false)
{
}

PyBimIfcImportReactor::PyBimIfcImportReactor(PyBimIfcImportReactorImpl* pObject, bool autoDelete)
    : m_pyImp(pObject, PySharedObjectDeleter<PyBimIfcImportReactorImpl>(autoDelete))
{
}

void PyBimIfcImportReactor::onStart(PyBrxBimIfcImportContext& context, const PyIfcEntity& project, const PyBrxBimIfcImportInfo& info)
{
    PyAutoLockGIL lock;
    try
    {
        if (const override& f = this->get_override("onStart"))
            f(context, project, info);
        else
            reg_onStart = false;
    }
    catch (...)
    {
        reg_onStart = false;
        printExceptionMsg();
    }
}

bool PyBimIfcImportReactor::onIfcProduct(PyBrxBimIfcImportContext& context, const PyIfcEntity& entity, bool isParent, const PyIfcEntity& parentEntity)
{
    PyAutoLockGIL lock;
    try
    {
        if (const override& f = this->get_override("onIfcProduct"))
            return f(context, entity, isParent, parentEntity);
        else
            reg_onIfcProduct = false;
    }
    catch (...)
    {
        reg_onIfcProduct = false;
        printExceptionMsg();
    }
    return false;
}

void PyBimIfcImportReactor::beforeCompletion(PyBrxBimIfcImportContext& context, bool success)
{
    PyAutoLockGIL lock;
    try
    {
        if (const override& f = this->get_override("beforeCompletion"))
            f(context, success);
        else
            reg_beforeCompletion = false;
    }
    catch (...)
    {
        reg_beforeCompletion = false;
        printExceptionMsg();
    }
}

void PyBimIfcImportReactor::onIfcProductImported(const PyIfcEntity& sourceEntity, bool isParent, const PyIfcEntity& sourceParentEntity, boost::python::list& createdAcEntites, const AcGeMatrix3d& xfrom)
{
    PyAutoLockGIL lock;
    try
    {
        if (const override& f = this->get_override("onIfcProductImported"))
            f(sourceEntity, isParent, sourceParentEntity, createdAcEntites, xfrom);
        else
            reg_onIfcProductImported = false;
    }
    catch (...)
    {
        reg_onIfcProductImported = false;
        printExceptionMsg();
    }
}

bool PyBimIfcImportReactor::attachReactor() const
{
    return impObj()->attachReactor();
}

bool PyBimIfcImportReactor::detachReactor() const
{
    return impObj()->detachReactor();
}

std::string PyBimIfcImportReactor::className()
{
    return "BimIfcImportReactor";
}

PyBimIfcImportReactorImpl* PyBimIfcImportReactor::impObj(const std::source_location& src /*= std::source_location::current()*/) const
{
    if (m_pyImp == nullptr) [[unlikely]] {
        throw PyNullObject(src);
    }
    return static_cast<PyBimIfcImportReactorImpl*>(m_pyImp.get());
}

//---------------------------------------------------------------------------------------- -
//PyBimIfcProjectData
void makePyBimIfcProjectDataWrapper()
{
    PyDocString DS("IfcProjectData");
    class_<PyBimIfcProjectData>("IfcProjectData")
        .def(init<>(DS.ARGS()))
        .def("getProjectName", &PyBimIfcProjectData::getProjectName, DS.ARGS())
        .def("setProjectName", &PyBimIfcProjectData::setProjectName, DS.ARGS({ "val:str" }))
        .def("getProjectDescription", &PyBimIfcProjectData::getProjectDescription, DS.ARGS())
        .def("setProjectDescription", &PyBimIfcProjectData::setProjectDescription, DS.ARGS({ "val:str" }))
        .def("getProjectPhase", &PyBimIfcProjectData::getProjectPhase, DS.ARGS())
        .def("setProjectPhase", &PyBimIfcProjectData::setProjectPhase, DS.ARGS({ "val:str" }))
        .def("getProjectNorthAngle", &PyBimIfcProjectData::getProjectNorthAngle, DS.ARGS())
        .def("setProjectNorthAngle", &PyBimIfcProjectData::setProjectNorthAngle, DS.ARGS({ "val:float" }))
        .def("getAuthorGivenName", &PyBimIfcProjectData::getAuthorGivenName, DS.ARGS())
        .def("setAuthorGivenName", &PyBimIfcProjectData::setAuthorGivenName, DS.ARGS({ "val:str" }))
        .def("getAuthorFamilyName", &PyBimIfcProjectData::getAuthorFamilyName, DS.ARGS())
        .def("setAuthorFamilyName", &PyBimIfcProjectData::setAuthorFamilyName, DS.ARGS({ "val:str" }))
        .def("getAuthorOrganization", &PyBimIfcProjectData::getAuthorOrganization, DS.ARGS())
        .def("setAuthorOrganization", &PyBimIfcProjectData::setAuthorOrganization, DS.ARGS({ "val:str" }))
        .def("getApplicationFullName", &PyBimIfcProjectData::getApplicationFullName, DS.ARGS())
        .def("setApplicationFullName", &PyBimIfcProjectData::setApplicationFullName, DS.ARGS({ "val:str" }))
        .def("getApplicationIdentifier", &PyBimIfcProjectData::getApplicationIdentifier, DS.ARGS())
        .def("setApplicationIdentifier", &PyBimIfcProjectData::setApplicationIdentifier, DS.ARGS({ "val:str" }))
        .def("getApplicationVersion", &PyBimIfcProjectData::getApplicationVersion, DS.ARGS())
        .def("setApplicationVersion", &PyBimIfcProjectData::setApplicationVersion, DS.ARGS({ "val:str" }))
        .def("getApplicationDeveloper", &PyBimIfcProjectData::getApplicationDeveloper, DS.ARGS())
        .def("setApplicationDeveloper", &PyBimIfcProjectData::setApplicationDeveloper, DS.ARGS({ "val:str" }))
        .def("getSiteName", &PyBimIfcProjectData::getSiteName, DS.ARGS())
        .def("setSiteName", &PyBimIfcProjectData::setSiteName, DS.ARGS({ "val:str" }))
        .def("getSiteDescription", &PyBimIfcProjectData::getSiteDescription, DS.ARGS())
        .def("setSiteDescription", &PyBimIfcProjectData::setSiteDescription, DS.ARGS({ "val:str" }))
        .def("getSiteLatitude", &PyBimIfcProjectData::getSiteLatitude, DS.ARGS())
        .def("setSiteLatitude", &PyBimIfcProjectData::setSiteLatitude, DS.ARGS({ "val:float" }))
        .def("getSiteLongitude", &PyBimIfcProjectData::getSiteLongitude, DS.ARGS())
        .def("setSitelongitude", &PyBimIfcProjectData::setSitelongitude, DS.ARGS({ "val:float" }))
        .def("getSiteElevation", &PyBimIfcProjectData::getSiteElevation, DS.ARGS())
        .def("setSiteElevation", &PyBimIfcProjectData::setSiteElevation, DS.ARGS({ "val:float" }))
        .def("getSiteLandTitleNumber", &PyBimIfcProjectData::getSiteLandTitleNumber, DS.ARGS())
        .def("setSiteLandTitleNumber", &PyBimIfcProjectData::setSiteLandTitleNumber, DS.ARGS({ "val:str" }))
        .def("getSiteInternalLocation", &PyBimIfcProjectData::getSiteInternalLocation, DS.ARGS())
        .def("setSiteInternalLocation", &PyBimIfcProjectData::setSiteInternalLocation, DS.ARGS({ "val:str" }))
        .def("getSitePostalBox", &PyBimIfcProjectData::getSitePostalBox, DS.ARGS())
        .def("setSitePostalBox", &PyBimIfcProjectData::setSitePostalBox, DS.ARGS({ "val:str" }))
        .def("getSiteTown", &PyBimIfcProjectData::getSiteTown, DS.ARGS())
        .def("setSiteTown", &PyBimIfcProjectData::setSiteTown, DS.ARGS({ "val:str" }))
        .def("getSiteRegion", &PyBimIfcProjectData::getSiteRegion, DS.ARGS())
        .def("setSiteRegion", &PyBimIfcProjectData::setSiteRegion, DS.ARGS({ "val:str" }))
        .def("getSitePostalCode", &PyBimIfcProjectData::getSitePostalCode, DS.ARGS())
        .def("setSitePostalCode", &PyBimIfcProjectData::setSitePostalCode, DS.ARGS({ "val:str" }))
        .def("getSiteCountry", &PyBimIfcProjectData::getSiteCountry, DS.ARGS())
        .def("setSiteCountry", &PyBimIfcProjectData::setSiteCountry, DS.ARGS({ "val:str" }))
        .def("getSiteAddressLines", &PyBimIfcProjectData::getSiteAddressLines, DS.ARGS())
        .def("setSiteAddressLines", &PyBimIfcProjectData::setSiteAddressLines, DS.ARGS({ "val:str" }))
        .def("getSiteBuildableArea", &PyBimIfcProjectData::getSiteBuildableArea, DS.ARGS())
        .def("setSiteBuildableArea", &PyBimIfcProjectData::setSiteBuildableArea, DS.ARGS({ "val:float" }))
        .def("getSiteTotalArea", &PyBimIfcProjectData::getSiteTotalArea, DS.ARGS())
        .def("setSiteTotalArea", &PyBimIfcProjectData::setSiteTotalArea, DS.ARGS({ "val:float" }))
        .def("getSiteBuildingHeightLimit", &PyBimIfcProjectData::getSiteBuildingHeightLimit, DS.ARGS())
        .def("setSiteBuildingHeightLimit", &PyBimIfcProjectData::setSiteBuildingHeightLimit, DS.ARGS({ "val:float" }))
        .def("className", &PyBimIfcProjectData::className, DS.SARGS()).staticmethod("className")
        ;
}

PyBimIfcProjectData::PyBimIfcProjectData(const BimApi::BimIfcProjectData& other)
    : impl(other)
{
}

std::string PyBimIfcProjectData::getProjectName() const
{
    return wstr_to_utf8(impl.project.name);
}

void PyBimIfcProjectData::setProjectName(const std::string& val)
{
    impl.project.name = utf8_to_wstr(val).c_str();
}

std::string PyBimIfcProjectData::getProjectDescription() const
{
    return wstr_to_utf8(impl.project.description);
}

void PyBimIfcProjectData::setProjectDescription(const std::string& val)
{
    impl.project.description = utf8_to_wstr(val).c_str();
}

std::string PyBimIfcProjectData::getProjectPhase() const
{
    return wstr_to_utf8(impl.project.phase);
}

void PyBimIfcProjectData::setProjectPhase(const std::string& val)
{
    impl.project.phase = utf8_to_wstr(val).c_str();
}

double PyBimIfcProjectData::getProjectNorthAngle() const
{
    return impl.project.northAngle;
}

void PyBimIfcProjectData::setProjectNorthAngle(double val)
{
    impl.project.northAngle = val;
}

std::string PyBimIfcProjectData::getAuthorGivenName() const
{
    return wstr_to_utf8(impl.author.givenName);
}

void PyBimIfcProjectData::setAuthorGivenName(const std::string& val)
{
    impl.author.givenName = utf8_to_wstr(val).c_str();
}

std::string PyBimIfcProjectData::getAuthorFamilyName() const
{
    return wstr_to_utf8(impl.author.familyName);
}

void PyBimIfcProjectData::setAuthorFamilyName(const std::string& val)
{
    impl.author.familyName = utf8_to_wstr(val).c_str();
}

std::string PyBimIfcProjectData::getAuthorOrganization() const
{
    return wstr_to_utf8(impl.author.organization);
}

void PyBimIfcProjectData::setAuthorOrganization(const std::string& val)
{
    impl.author.organization = utf8_to_wstr(val).c_str();
}

std::string PyBimIfcProjectData::getApplicationFullName() const
{
    return wstr_to_utf8(impl.application.fullName);
}

void PyBimIfcProjectData::setApplicationFullName(const std::string& val)
{
    impl.application.fullName = utf8_to_wstr(val).c_str();
}

std::string PyBimIfcProjectData::getApplicationIdentifier() const
{
    return wstr_to_utf8(impl.application.identifier);
}

void PyBimIfcProjectData::setApplicationIdentifier(const std::string& val)
{
    impl.application.identifier = utf8_to_wstr(val).c_str();
}

std::string PyBimIfcProjectData::getApplicationVersion() const
{
    return wstr_to_utf8(impl.application.version);
}

void PyBimIfcProjectData::setApplicationVersion(const std::string& val)
{
    impl.application.version = utf8_to_wstr(val).c_str();
}

std::string PyBimIfcProjectData::getApplicationDeveloper() const
{
    return wstr_to_utf8(impl.application.developer);
}

void PyBimIfcProjectData::setApplicationDeveloper(const std::string& val)
{
    impl.application.developer = utf8_to_wstr(val).c_str();
}

std::string PyBimIfcProjectData::getSiteName() const
{
    return wstr_to_utf8(impl.site.name);
}

void PyBimIfcProjectData::setSiteName(const std::string& val)
{
    impl.site.name = utf8_to_wstr(val).c_str();
}

std::string PyBimIfcProjectData::getSiteDescription() const
{
    return wstr_to_utf8(impl.site.description);
}

void PyBimIfcProjectData::setSiteDescription(const std::string& val)
{
    impl.site.description = utf8_to_wstr(val).c_str();
}

double PyBimIfcProjectData::getSiteLatitude() const
{
    return impl.site.latitude;
}

void PyBimIfcProjectData::setSiteLatitude(double val)
{
    impl.site.latitude = val;
}

double PyBimIfcProjectData::getSiteLongitude() const
{
    return impl.site.longitude;
}

void PyBimIfcProjectData::setSitelongitude(double val)
{
    impl.site.longitude = val;
}

double PyBimIfcProjectData::getSiteElevation() const
{
    return impl.site.elevation;
}

void PyBimIfcProjectData::setSiteElevation(double val)
{
    impl.site.elevation = val;
}

std::string PyBimIfcProjectData::getSiteLandTitleNumber() const
{
    return wstr_to_utf8(impl.site.landTitleNumber);
}

void PyBimIfcProjectData::setSiteLandTitleNumber(const std::string& val)
{
    impl.site.landTitleNumber = utf8_to_wstr(val).c_str();
}

std::string PyBimIfcProjectData::getSiteInternalLocation() const
{
    return wstr_to_utf8(impl.site.internalLocation);
}

void PyBimIfcProjectData::setSiteInternalLocation(const std::string& val)
{
    impl.site.internalLocation = utf8_to_wstr(val).c_str();
}

std::string PyBimIfcProjectData::getSitePostalBox() const
{
    return wstr_to_utf8(impl.site.postalBox);
}

void PyBimIfcProjectData::setSitePostalBox(const std::string& val)
{
    impl.site.postalBox = utf8_to_wstr(val).c_str();
}

std::string PyBimIfcProjectData::getSiteTown() const
{
    return wstr_to_utf8(impl.site.town);
}

void PyBimIfcProjectData::setSiteTown(const std::string& val)
{
    impl.site.town = utf8_to_wstr(val).c_str();
}

std::string PyBimIfcProjectData::getSiteRegion() const
{
    return wstr_to_utf8(impl.site.region);
}

void PyBimIfcProjectData::setSiteRegion(const std::string& val)
{
    impl.site.region = utf8_to_wstr(val).c_str();
}

std::string PyBimIfcProjectData::getSitePostalCode() const
{
    return wstr_to_utf8(impl.site.postalCode);
}

void PyBimIfcProjectData::setSitePostalCode(const std::string& val)
{
    impl.site.postalCode = utf8_to_wstr(val).c_str();
}

std::string PyBimIfcProjectData::getSiteCountry() const
{
    return wstr_to_utf8(impl.site.country);
}

void PyBimIfcProjectData::setSiteCountry(const std::string& val)
{
    impl.site.country = utf8_to_wstr(val).c_str();
}

std::string PyBimIfcProjectData::getSiteAddressLines() const
{
    return wstr_to_utf8(impl.site.adressLines);
}

void PyBimIfcProjectData::setSiteAddressLines(const std::string& val)
{
    impl.site.adressLines = utf8_to_wstr(val).c_str();
}

double PyBimIfcProjectData::getSiteBuildableArea() const
{
    return impl.site.buildableArea;
}

void PyBimIfcProjectData::setSiteBuildableArea(double val)
{
    impl.site.buildableArea = val;
}

double PyBimIfcProjectData::getSiteTotalArea() const
{
    return impl.site.totalArea;
}

void PyBimIfcProjectData::setSiteTotalArea(double val)
{
    impl.site.totalArea = val;
}

double PyBimIfcProjectData::getSiteBuildingHeightLimit() const
{
    return impl.site.buildingHeightLimit;
}

void PyBimIfcProjectData::setSiteBuildingHeightLimit(double val)
{
    impl.site.buildingHeightLimit = val;
}

std::string PyBimIfcProjectData::className()
{
    return "BimIfcProjectData";
}

//---------------------------------------------------------------------------------------- -
//BrxBimIfcExportContext
void makePyBrxBimIfcExportContextWrapper()
{
    constexpr const std::string_view setIfcRootDataOverloads = "Overloads:\n"
        "- ifcObject: PyBrxBim.IfcEntity\n"
        "- ifcObject: PyBrxBim.IfcEntity, name:str, description:str, guid:str, hist: PyBrxBim.IfcEntity\n";

    PyDocString DS("IfcExportContext");
    class_<PyBrxBimIfcExportContext>("IfcExportContext", boost::python::no_init)
        .def("ifcModel", &PyBrxBimIfcExportContext::ifcModel, DS.ARGS())
        .def("database", &PyBrxBimIfcExportContext::database, DS.ARGS())
        .def("getProduct", &PyBrxBimIfcExportContext::getProduct1)
        .def("getProduct", &PyBrxBimIfcExportContext::getProduct2, DS.ARGS({ "val:PyDb.ObjectId|PyDb.FullSubentPath" }))
        .def("setIfcRootData", &PyBrxBimIfcExportContext::setIfcRootData1)
        .def("setIfcRootData", &PyBrxBimIfcExportContext::setIfcRootData2, DS.OVRL(setIfcRootDataOverloads))
        .def("setLocationRelToWCS", &PyBrxBimIfcExportContext::setLocationRelToWCS,
            DS.ARGS({ "ifcObject: PyBrxBim.IfcEntity","relativeCoordSys: PyGe.Matrix3d" }))
        .def("setLocationRelToAssignedSpatialLocation", &PyBrxBimIfcExportContext::setLocationRelToAssignedSpatialLocation,
            DS.ARGS({ "ifcElement: PyBrxBim.IfcEntity","correspondingEntity: PyDb.Entity","relativeCoordSys: PyGe.Matrix3d" }))
        .def("setLocationRelToBuilding", &PyBrxBimIfcExportContext::setLocationRelToBuilding,
            DS.ARGS({ "ifcElement: PyBrxBim.IfcEntity","buildingName: str","relativeCoordSys: PyGe.Matrix3d" }))
        .def("setLocationRelToStory", &PyBrxBimIfcExportContext::setLocationRelToStory,
            DS.ARGS({ "ifcElement: PyBrxBim.IfcEntity","buildingName: str","storyName: str","relativeCoordSys: PyGe.Matrix3d" }))
        .def("setRepresentationAsExtrudedAreaSolid", &PyBrxBimIfcExportContext::setRepresentationAsExtrudedAreaSolid,
            DS.ARGS({ "ifcProduct: PyBrxBim.IfcEntity","correspondingSolid: PyDb.Solid3d","preferredSweepingDirections: PyGe.Vector3d" }))
        .def("setRepresentationAsClippedExtrudedAreaSolid", &PyBrxBimIfcExportContext::setRepresentationAsClippedExtrudedAreaSolid,
            DS.ARGS({ "ifcProduct: PyBrxBim.IfcEntity","correspondingSolid: PyDb.Solid3d","extrusionDirection: PyGe.Vector3d" }))
        .def("setRepresentationAsBrep", &PyBrxBimIfcExportContext::setRepresentationAsBrep,
            DS.ARGS({ "ifcProduct: PyBrxBim.IfcEntity","correspondingEntity: PyDb.Entity" }))
        .def("setMaterialToAssignedComposition", &PyBrxBimIfcExportContext::setMaterialToAssignedComposition,
            DS.ARGS({ "ifcObject: PyBrxBim.IfcEntity","correspondingEntity: PyDb.Entity","thicknessVariableLayer: float" }))
        .def("setMaterialToComposition", &PyBrxBimIfcExportContext::setMaterialToComposition,
            DS.ARGS({ "ifcObject: PyBrxBim.IfcEntity","compositionName: str","thicknessVariableLayer: float" }))
        .def("getAxis2Placement2D", &PyBrxBimIfcExportContext::getAxis2Placement2D, DS.ARGS({ "coordSystem:PyGe.Matrix2d" }))
        .def("getAxis2Placement3D", &PyBrxBimIfcExportContext::getAxis2Placement3D, DS.ARGS({ "coordSystem:PyGe.Matrix3d" }))
        .def("getCartesianPoint2D", &PyBrxBimIfcExportContext::getCartesianPoint2D, DS.ARGS({ "pt:PyGe.Point2d" }))
        .def("getCartesianPoint3D", &PyBrxBimIfcExportContext::getCartesianPoint3D, DS.ARGS({ "pt:PyGe.Point3d" }))
        .def("getDirection2D", &PyBrxBimIfcExportContext::getDirection2D, DS.ARGS({ "vec:PyGe.Vector3d" }))
        .def("getDirection3D", &PyBrxBimIfcExportContext::getDirection3D, DS.ARGS({ "vec:PyGe.Vector3d" }))
        .def("className", &PyBrxBimIfcExportContext::className, DS.SARGS()).staticmethod("className")
        ;
}

PyBrxBimIfcExportContext::PyBrxBimIfcExportContext(const IfcExportContext* pObject)
    :PyBrxBimIfcExportContext(const_cast<IfcExportContext*>(pObject), false)
{
}

PyBrxBimIfcExportContext::PyBrxBimIfcExportContext(IfcExportContext* pObject, bool autoDelete)
    : m_pyImp(pObject, PySharedObjectDeleter<IfcExportContext>(autoDelete))
{
}

PyIfcModel PyBrxBimIfcExportContext::ifcModel() const
{
    return PyIfcModel{ impObj()->ifcModel(),false };
}

PyDbDatabase PyBrxBimIfcExportContext::database() const
{
    return PyDbDatabase{ impObj()->database() };
}

PyIfcEntity PyBrxBimIfcExportContext::getProduct1(const PyDbObjectId& id) const
{
    return PyIfcEntity{ impObj()->getProduct(id.m_id) };
}

PyIfcEntity PyBrxBimIfcExportContext::getProduct2(const PyDbFullSubentPath& idSubent) const
{
    return PyIfcEntity{ impObj()->getProduct(idSubent.pyImp) };
}

bool PyBrxBimIfcExportContext::setIfcRootData1(const PyIfcEntity& ifcObject) const
{
    return impObj()->setIfcRootData(*ifcObject.impObj());
}

bool PyBrxBimIfcExportContext::setIfcRootData2(const PyIfcEntity& ifcObject, const std::string& name, const std::string& description, const std::string& guid, const PyIfcEntity& pHist) const
{
    return impObj()->setIfcRootData(*ifcObject.impObj(), utf8_to_wstr(name).c_str(), utf8_to_wstr(description).c_str(), utf8_to_wstr(guid).c_str(), pHist.m_pyImp.get());
}

bool PyBrxBimIfcExportContext::setLocationRelToWCS(const PyIfcEntity& ifcProduct, const AcGeMatrix3d& relativeCoordSys) const
{
    return impObj()->setLocationRelToWCS(*ifcProduct.impObj(), &relativeCoordSys);
}

bool PyBrxBimIfcExportContext::setLocationRelToAssignedSpatialLocation(const PyIfcEntity& ifcElement, const PyDbEntity& correspondingEntity, const AcGeMatrix3d& relativeCoordSys) const
{
    return impObj()->setLocationRelToAssignedSpatialLocation(*ifcElement.impObj(), correspondingEntity.impObj(), &relativeCoordSys);
}

bool PyBrxBimIfcExportContext::setLocationRelToBuilding(const PyIfcEntity& ifcElement, const std::string& buildingName, const AcGeMatrix3d& relativeCoordSys) const
{
    return impObj()->setLocationRelToBuilding(*ifcElement.impObj(), utf8_to_wstr(buildingName).c_str(), &relativeCoordSys);
}

bool PyBrxBimIfcExportContext::setLocationRelToStory(const PyIfcEntity& ifcElement, const std::string& buildingName, const std::string& storyName, const AcGeMatrix3d& relativeCoordSys) const
{
    return impObj()->setLocationRelToStory(*ifcElement.impObj(), utf8_to_wstr(buildingName).c_str(), utf8_to_wstr(storyName).c_str(), &relativeCoordSys);
}

bool PyBrxBimIfcExportContext::setRepresentationAsExtrudedAreaSolid(const PyIfcEntity& ifcProduct, const PyDb3dSolid& correspondingSolid, const AcGeVector3d& preferredSweepingDirections) const
{
    return impObj()->setRepresentationAsExtrudedAreaSolid(*ifcProduct.impObj(), correspondingSolid.impObj(), preferredSweepingDirections);
}

bool PyBrxBimIfcExportContext::setRepresentationAsClippedExtrudedAreaSolid(const PyIfcEntity& ifcProduct, const PyDb3dSolid& correspondingSolid, const AcGeVector3d& extrusionDirection) const
{
    return impObj()->setRepresentationAsClippedExtrudedAreaSolid(*ifcProduct.impObj(), correspondingSolid.impObj(), extrusionDirection);
}

bool PyBrxBimIfcExportContext::setRepresentationAsBrep(PyIfcEntity& ifcProduct, const PyDbEntity& correspondingEntity) const
{
    return impObj()->setRepresentationAsBrep(*ifcProduct.impObj(), correspondingEntity.impObj());
}

bool PyBrxBimIfcExportContext::setMaterialToAssignedComposition(const PyIfcEntity& ifcObject, const PyDbEntity& correspondingEntity, double thicknessVariableLayer) const
{
    return impObj()->setMaterialToAssignedComposition(*ifcObject.impObj(), correspondingEntity.impObj(), thicknessVariableLayer);
}

bool PyBrxBimIfcExportContext::setMaterialToComposition(const PyIfcEntity& ifcObject, const std::string& compositionName, double thicknessVariableLayer) const
{
    return impObj()->setMaterialToComposition(*ifcObject.impObj(), utf8_to_wstr(compositionName).c_str(), thicknessVariableLayer);
}

PyIfcEntity PyBrxBimIfcExportContext::getAxis2Placement2D(const AcGeMatrix2d& coordSystem) const
{
    return PyIfcEntity{ impObj()->getAxis2Placement2D(coordSystem) };
}

PyIfcEntity PyBrxBimIfcExportContext::getAxis2Placement3D(const AcGeMatrix3d& coordSystem) const
{
    return PyIfcEntity{ impObj()->getAxis2Placement3D(coordSystem) };
}

PyIfcEntity PyBrxBimIfcExportContext::getCartesianPoint2D(const AcGePoint2d& pt) const
{
    return PyIfcEntity{ impObj()->getCartesianPoint2D(pt) };
}

PyIfcEntity PyBrxBimIfcExportContext::getCartesianPoint3D(const AcGePoint3d& pt) const
{
    return PyIfcEntity{ impObj()->getCartesianPoint3D(pt) };
}

PyIfcEntity PyBrxBimIfcExportContext::getDirection2D(const AcGeVector2d& vec) const
{
    return PyIfcEntity{ impObj()->getDirection2D(vec) };
}

PyIfcEntity PyBrxBimIfcExportContext::getDirection3D(const AcGeVector3d& vec) const
{
    return PyIfcEntity{ impObj()->getDirection3D(vec) };
}

std::string PyBrxBimIfcExportContext::className()
{
    return "BimIfcExportContext";
}

IfcExportContext* PyBrxBimIfcExportContext::impObj(const std::source_location& src /*= std::source_location::current()*/) const
{
    if (m_pyImp == nullptr) [[unlikely]] {
        throw PyNullObject(src);
    }
    return m_pyImp.get();
}

//---------------------------------------------------------------------------------------- -
//PyBrxIfcExportOptions
void makePyBrxIfcExportOptionsWrapper()
{

    PyDocString DS("IfcExportOptions");
    class_<PyBrxIfcExportOptions>("IfcExportOptions")
        .def(init<>(DS.ARGS()))

#if defined(_BRXTARGET) && (_BRXTARGET >= 250)
        .def("optionFlags", &PyBrxIfcExportOptions::optionFlags, DS.ARGS())
        .def("setOptionFlags", &PyBrxIfcExportOptions::setOptionFlags, DS.ARGS({ "val:int" }))
        .def("option", &PyBrxIfcExportOptions::option, DS.ARGS())
        .def("setOption", &PyBrxIfcExportOptions::setOption, DS.ARGS({ "option:PyBrxBim.IfcExportOptionFlags", "value:bool" }))
#endif
        .def("objectsToExport", &PyBrxIfcExportOptions::objectsToExport, DS.ARGS())
        .def("setObjectsToExport", &PyBrxIfcExportOptions::setObjectsToExport, DS.ARGS({ "ids:list[PyDb.ObjectId]" }))
        .def("nestedObjectsToExport", &PyBrxIfcExportOptions::nestedObjectsToExport, DS.ARGS())
        .def("setNestedObjectsToExport", &PyBrxIfcExportOptions::setNestedObjectsToExport, DS.ARGS({ "ids:list[PyDb.FullSubentPath]" }))
        .def("ifcVersion", &PyBrxIfcExportOptions::ifcVersion, DS.ARGS())
        .def("setIfcVersion", &PyBrxIfcExportOptions::setIfcVersion, DS.ARGS({ "val:PyBrxBim.IfcSchemaId" }))
        .def("mvdType", &PyBrxIfcExportOptions::mvdType, DS.ARGS())
        .def("setMvdType", &PyBrxIfcExportOptions::setMvdType, DS.ARGS({ "val:PyBrxBim.IfcModelViewDefType" }))
        .def("exportIfcFile", &PyBrxIfcExportOptions::exportIfcFile1)
        .def("exportIfcFile", &PyBrxIfcExportOptions::exportIfcFile2, DS.SARGS({ "db: PyAp.Document", "filename: str", "options: PyBrxBim.IfcExportOptions = ..." })).staticmethod("exportIfcFile")
        .def("className", &PyBrxIfcExportOptions::className, DS.SARGS()).staticmethod("className")
        ;
}

PyBrxIfcExportOptions::PyBrxIfcExportOptions()
    : m_pyImp(new BimApi::BrxIfcExportOptions())
{
}

PyBrxIfcExportOptions::PyBrxIfcExportOptions(const BimApi::BrxIfcExportOptions& other)
    : m_pyImp(new BimApi::BrxIfcExportOptions(other))
{
}

#if defined(_BRXTARGET) && (_BRXTARGET >= 250)
Adesk::UInt32 PyBrxIfcExportOptions::optionFlags() const
{
    return impObj()->optionFlags();
}
#endif

#if defined(_BRXTARGET) && (_BRXTARGET >= 250)
void PyBrxIfcExportOptions::setOptionFlags(Adesk::UInt32 options) const
{
    impObj()->setOptionFlags(options);
}
#endif

#if defined(_BRXTARGET) && (_BRXTARGET >= 250)
bool PyBrxIfcExportOptions::option(BimApi::BrxIfcExportOptions::EOptionFlags option) const
{
    return impObj()->option(option);
}
#endif

#if defined(_BRXTARGET) && (_BRXTARGET >= 250)
void PyBrxIfcExportOptions::setOption(BimApi::BrxIfcExportOptions::EOptionFlags option, bool value) const
{
    impObj()->setOption(option, value);
}
#endif

boost::python::list PyBrxIfcExportOptions::objectsToExport() const
{
    return ObjectIdArrayToPyList(impObj()->objectsToExport());
}

void PyBrxIfcExportOptions::setObjectsToExport(const boost::python::list& arObjectsForExport) const
{
    impObj()->setObjectsToExport(PyListToObjectIdArray(arObjectsForExport));
}

boost::python::list PyBrxIfcExportOptions::nestedObjectsToExport() const
{
    return FullSubentPathArrayToPyList(impObj()->nestedObjectsToExport());
}

void PyBrxIfcExportOptions::setNestedObjectsToExport(const boost::python::list& arObjectsForExport) const
{
    impObj()->setNestedObjectsToExport(PyListToPyDbFullSubentPathArray(arObjectsForExport));
}

Ice::EIfcSchemaId PyBrxIfcExportOptions::ifcVersion() const
{
    return impObj()->ifcVersion();
}

void PyBrxIfcExportOptions::setIfcVersion(Ice::EIfcSchemaId eSchemaId) const
{
    impObj()->setIfcVersion(eSchemaId);
}

BimApi::BrxIfcExportOptions::EModelViewDefType PyBrxIfcExportOptions::mvdType() const
{
    return impObj()->mvdType();
}

void PyBrxIfcExportOptions::setMvdType(BimApi::BrxIfcExportOptions::EModelViewDefType eType) const
{
    impObj()->setMvdType(eType);
}

void PyBrxIfcExportOptions::exportIfcFile1(const PyApDocument& pDoc, const std::string& filename)
{
    PyThrowBadBim(BimApi::exportIfcFile(pDoc.impObj(), utf8_to_wstr(filename).c_str()));
}

void PyBrxIfcExportOptions::exportIfcFile2(const PyApDocument& pDoc, const std::string& filename, const PyBrxIfcExportOptions& pOptions)
{
    PyThrowBadBim(BimApi::exportIfcFile(pDoc.impObj(), utf8_to_wstr(filename).c_str(), pOptions.impObj()));
}

std::string PyBrxIfcExportOptions::className()
{
    return "BrxIfcExportOptions";
}

BimApi::BrxIfcExportOptions* PyBrxIfcExportOptions::impObj(const std::source_location& src /*= std::source_location::current()*/) const
{
    if (m_pyImp == nullptr) [[unlikely]] {
        throw PyNullObject(src);
    }
    return m_pyImp.get();
}

//---------------------------------------------------------------------------------------- -
//PyBimIfcExportReactorImpl
PyBimIfcExportReactorImpl::PyBimIfcExportReactorImpl(PyBimIfcExportReactor* ptr, const AcString& displayName, const AcString& guid)
    : m_pyBackPtr(ptr), m_displayName(displayName), m_guid(guid)
{
    m_instance = this;
}

void PyBimIfcExportReactorImpl::adjustProjectData(Context& context, BimApi::BimIfcProjectData& projectData)
{
    if (impObj()->reg_adjustProjectData)
    {
        PyBrxBimIfcExportContext ctx(std::addressof(context));
        PyBimIfcProjectData data(projectData);
        impObj()->adjustProjectData(ctx, data);
    }
}

void PyBimIfcExportReactorImpl::onBeginIfcModelSetup(Context& context)
{
    if (impObj()->reg_onBeginIfcModelSetup)
    {
        PyBrxBimIfcExportContext ctx(std::addressof(context));
        impObj()->onBeginIfcModelSetup(ctx);
    }
}

Ice::IfcApi::Entity PyBimIfcExportReactorImpl::onEntity(Context& context, AcDbEntity* pEntity)
{
    Ice::IfcApi::Entity ent{};
    if (impObj()->reg_onEntity)
    {
        PyBrxBimIfcExportContext ctx(std::addressof(context));
        PyDbEntity ent(pEntity, false);
        return Ice::IfcApi::Entity(*impObj()->onEntity(ctx, ent).impObj());
    }
    return Ice::IfcApi::Entity::s_null;
}

void PyBimIfcExportReactorImpl::onEndIfcModelSetup(Context& context)
{
    if (impObj()->reg_onEndIfcModelSetup)
    {
        PyBrxBimIfcExportContext ctx(std::addressof(context));
        impObj()->onEndIfcModelSetup(ctx);
    }
}

void PyBimIfcExportReactorImpl::onEntityConstructed(Ice::IfcApi::Entity& contructedEntity, AcDbEntity* pSourceBCEntity)
{
    if (impObj()->reg_onEndIfcModelSetup)
    {
        PyIfcEntity _contructedEntity(std::addressof(contructedEntity));
        PyDbEntity _pSourceBCEntity(pSourceBCEntity, false);
        impObj()->onEntityConstructed(_contructedEntity, _pSourceBCEntity);
    }
}

BimIfcExportReactorInstance* PyBimIfcExportReactorImpl::getIfcReactorInstance(Ice::EIfcSchemaId schema)
{
    return m_instance;
}

const ACHAR* PyBimIfcExportReactorImpl::GUID() const
{
    return m_guid;
}

const ACHAR* PyBimIfcExportReactorImpl::displayName() const
{
    return m_displayName;
}

PyBimIfcExportReactor* PyBimIfcExportReactorImpl::impObj(const std::source_location& src /*= std::source_location::current()*/) const
{
    if (m_pyBackPtr == nullptr) [[unlikely]] {
        throw PyNullObject(src);
    }
    return m_pyBackPtr;
}

//---------------------------------------------------------------------------------------- -
//BimIfcExportReactor
void makePyBimIfcExportReactorWrapper()
{
    PyDocString DS("IfcExportReactor");
    class_<PyBimIfcExportReactor>("IfcExportReactor", boost::python::no_init)
        .def(init<const std::string&, const std::string&>(DS.ARGS({ "displayName: str","guid: str" })))

        .def("adjustProjectData", &PyBimIfcExportReactor::adjustProjectData, DS.ARGS({ "context: PyBrxBim.IfcExportContext", "project: PyBrxBim.IfcProjectData"}))
        .def("onBeginIfcModelSetup", &PyBimIfcExportReactor::onBeginIfcModelSetup, DS.ARGS({ "context: PyBrxBim.IfcExportContext"}))
        .def("onEntity", &PyBimIfcExportReactor::onEntity, DS.ARGS({ "context: PyBrxBim.IfcExportContext", "entity: PyDb.Entity" }))
        .def("onEndIfcModelSetup", &PyBimIfcExportReactor::onEndIfcModelSetup, DS.ARGS({ "context: PyBrxBim.IfcExportContext" }))
        .def("onEntityConstructed", &PyBimIfcExportReactor::onEntityConstructed, DS.ARGS({ "contructedEntity: PyBrxBim.IfcEntity", "sourceBCEntity: PyDb.Entity" }))

        .def("attachReactor", &PyBimIfcExportReactor::attachReactor, DS.ARGS())
        .def("detachReactor", &PyBimIfcExportReactor::detachReactor, DS.ARGS())
        .def("className", &PyBimIfcExportReactor::className, DS.SARGS()).staticmethod("className")
        ;
}

PyBimIfcExportReactor::PyBimIfcExportReactor(const std::string& displayName, const std::string& GUID)
    : PyBimIfcExportReactor(new PyBimIfcExportReactorImpl(this, utf8_to_wstr(GUID).c_str(), utf8_to_wstr(displayName).c_str()), true)
{

}

PyBimIfcExportReactor::PyBimIfcExportReactor(const PyBimIfcExportReactorImpl* pObject)
    :PyBimIfcExportReactor(const_cast<PyBimIfcExportReactorImpl*>(pObject), false)
{
}

PyBimIfcExportReactor::PyBimIfcExportReactor(PyBimIfcExportReactorImpl* pObject, bool autoDelete)
    : m_pyImp(pObject, PySharedObjectDeleter<PyBimIfcExportReactorImpl>(autoDelete))
{
}


bool PyBimIfcExportReactor::attachReactor() const
{
    return impObj()->attachReactor();
}

bool PyBimIfcExportReactor::detachReactor() const
{
    return impObj()->detachReactor();
}

void PyBimIfcExportReactor::adjustProjectData(PyBrxBimIfcExportContext& context, PyBimIfcProjectData& projectData)
{
    PyAutoLockGIL lock;
    try
    {
        if (const override& f = this->get_override("adjustProjectData"))
            f(context, projectData);
        else
            reg_adjustProjectData = false;
    }
    catch (...)
    {
        reg_adjustProjectData = false;
        printExceptionMsg();
    }
}

void PyBimIfcExportReactor::onBeginIfcModelSetup(PyBrxBimIfcExportContext& context)
{
    PyAutoLockGIL lock;
    try
    {
        if (const override& f = this->get_override("onBeginIfcModelSetup"))
            f(context);
        else
            reg_onBeginIfcModelSetup = false;
    }
    catch (...)
    {
        reg_onBeginIfcModelSetup = false;
        printExceptionMsg();
    }
}

PyIfcEntity PyBimIfcExportReactor::onEntity(PyBrxBimIfcExportContext& context, PyDbEntity& pEntity)
{
    PyAutoLockGIL lock;
    try
    {
        if (const override& f = this->get_override("onEntity"))
            return f(context, pEntity);
        else
            reg_onEntity = false;
    }
    catch (...)
    {
        reg_onEntity = false;
        printExceptionMsg();
    }
    return PyIfcEntity{};
}

void PyBimIfcExportReactor::onEndIfcModelSetup(PyBrxBimIfcExportContext& context)
{
    PyAutoLockGIL lock;
    try
    {
        if (const override& f = this->get_override("onEndIfcModelSetup"))
            f(context);
        else
            reg_onEndIfcModelSetup = false;
    }
    catch (...)
    {
        reg_onEndIfcModelSetup = false;
        printExceptionMsg();
    }
}

void PyBimIfcExportReactor::onEntityConstructed(PyIfcEntity& contructedEntity, PyDbEntity& pSourceBCEntity)
{
    PyAutoLockGIL lock;
    try
    {
        if (const override& f = this->get_override("onEntityConstructed"))
            f(contructedEntity, pSourceBCEntity);
        else
            reg_onEntityConstructed = false;
    }
    catch (...)
    {
        reg_onEntityConstructed = false;
        printExceptionMsg();
    }
}

std::string PyBimIfcExportReactor::className()
{
    return "BimIfcExportReactor";
}

PyBimIfcExportReactorImpl* PyBimIfcExportReactor::impObj(const std::source_location& src /*= std::source_location::current()*/) const
{
    if (m_pyImp == nullptr) [[unlikely]] {
        throw PyNullObject(src);
    }
    return static_cast<PyBimIfcExportReactorImpl*>(m_pyImp.get());
}

#endif
