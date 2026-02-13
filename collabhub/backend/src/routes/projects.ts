import express from 'express';
import { authenticate, AuthRequest } from '../middleware/auth';
import prisma from '../config/database';
import { createProjectSchema } from '../utils/validation';
import { AppError } from '../middleware/errorHandler';

const router = express.Router();

// All routes require authentication
router.use(authenticate);

router.get('/', async (req: AuthRequest, res, next) => {
  try {
    const projects = await prisma.project.findMany({
      where: {
        OR: [
          { ownerId: req.user!.id },
          { members: { some: { userId: req.user!.id } } },
        ],
      },
      include: {
        owner: {
          select: { id: true, name: true, email: true, avatar: true },
        },
        members: {
          include: {
            user: {
              select: { id: true, name: true, email: true, avatar: true },
            },
          },
        },
        _count: {
          select: { tasks: true },
        },
      },
      orderBy: { updatedAt: 'desc' },
    });

    res.json(projects);
  } catch (error) {
    next(error);
  }
});

router.get('/:id', async (req: AuthRequest, res, next) => {
  try {
    const project = await prisma.project.findFirst({
      where: {
        id: req.params.id,
        OR: [
          { ownerId: req.user!.id },
          { members: { some: { userId: req.user!.id } } },
        ],
      },
      include: {
        owner: {
          select: { id: true, name: true, email: true, avatar: true },
        },
        members: {
          include: {
            user: {
              select: { id: true, name: true, email: true, avatar: true },
            },
          },
        },
        tasks: {
          include: {
            assignee: {
              select: { id: true, name: true, email: true, avatar: true },
            },
            _count: {
              select: { comments: true, attachments: true },
            },
          },
          orderBy: { createdAt: 'desc' },
        },
      },
    });

    if (!project) {
      throw new AppError('Project not found', 404);
    }

    res.json(project);
  } catch (error) {
    next(error);
  }
});

router.post('/', async (req: AuthRequest, res, next) => {
  try {
    const validatedData = createProjectSchema.parse(req.body);

    const project = await prisma.project.create({
      data: {
        name: validatedData.name,
        description: validatedData.description,
        color: validatedData.color,
        ownerId: req.user!.id,
        members: {
          create: {
            userId: req.user!.id,
            role: 'owner',
          },
        },
      },
      include: {
        owner: {
          select: { id: true, name: true, email: true, avatar: true },
        },
        members: {
          include: {
            user: {
              select: { id: true, name: true, email: true, avatar: true },
            },
          },
        },
      },
    });

    res.status(201).json(project);
  } catch (error) {
    next(error);
  }
});

router.put('/:id', async (req: AuthRequest, res, next) => {
  try {
    const project = await prisma.project.findFirst({
      where: {
        id: req.params.id,
        OR: [
          { ownerId: req.user!.id },
          { members: { some: { userId: req.user!.id, role: { in: ['owner', 'admin'] } } } },
        ],
      },
    });

    if (!project) {
      throw new AppError('Project not found or insufficient permissions', 404);
    }

    const validatedData = createProjectSchema.partial().parse(req.body);

    const updatedProject = await prisma.project.update({
      where: { id: req.params.id },
      data: validatedData,
      include: {
        owner: {
          select: { id: true, name: true, email: true, avatar: true },
        },
        members: {
          include: {
            user: {
              select: { id: true, name: true, email: true, avatar: true },
            },
          },
        },
      },
    });

    res.json(updatedProject);
  } catch (error) {
    next(error);
  }
});

router.delete('/:id', async (req: AuthRequest, res, next) => {
  try {
    const project = await prisma.project.findFirst({
      where: {
        id: req.params.id,
        ownerId: req.user!.id,
      },
    });

    if (!project) {
      throw new AppError('Project not found or insufficient permissions', 404);
    }

    await prisma.project.delete({
      where: { id: req.params.id },
    });

    res.json({ message: 'Project deleted successfully' });
  } catch (error) {
    next(error);
  }
});

router.post('/:id/members', async (req: AuthRequest, res, next) => {
  try {
    const { userId, role = 'member' } = req.body;

    if (!userId) {
      throw new AppError('User ID is required', 400);
    }

    const project = await prisma.project.findFirst({
      where: {
        id: req.params.id,
        OR: [
          { ownerId: req.user!.id },
          { members: { some: { userId: req.user!.id, role: { in: ['owner', 'admin'] } } } },
        ],
      },
    });

    if (!project) {
      throw new AppError('Project not found or insufficient permissions', 404);
    }

    const member = await prisma.projectMember.create({
      data: {
        userId,
        projectId: req.params.id,
        role,
      },
      include: {
        user: {
          select: { id: true, name: true, email: true, avatar: true },
        },
      },
    });

    res.status(201).json(member);
  } catch (error) {
    next(error);
  }
});

router.delete('/:id/members/:memberId', async (req: AuthRequest, res, next) => {
  try {
    const project = await prisma.project.findFirst({
      where: {
        id: req.params.id,
        OR: [
          { ownerId: req.user!.id },
          { members: { some: { userId: req.user!.id, role: { in: ['owner', 'admin'] } } } },
        ],
      },
    });

    if (!project) {
      throw new AppError('Project not found or insufficient permissions', 404);
    }

    await prisma.projectMember.delete({
      where: { id: req.params.memberId },
    });

    res.json({ message: 'Member removed successfully' });
  } catch (error) {
    next(error);
  }
});

export default router;
